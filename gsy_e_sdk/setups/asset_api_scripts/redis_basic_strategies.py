"""
Template file for a trading strategy through the gsy-e-sdk api client using Redis.
"""

from time import sleep
from typing import List, Dict
from gsy_e_sdk.redis_aggregator import RedisAggregator
from gsy_e_sdk.redis_bc_aggregator import RedisBCAggregator
from gsy_e_sdk.clients.redis_asset_client import RedisAssetClient
import b4p 
if not b4p.started():
    b4p.init()
ORACLE_NAME = "oracle"

# List of assets' names to be connected with the API
LOAD_NAMES = ["Load 1 L13", "Load 2 L21", "Load 3 L17"]
PV_NAMES = ["PV 1 (4kW)", "PV 3 (5kW)"]
STORAGE_NAMES = ["Tesla Powerwall 3"]

# Frequency of bids/offers posting in a market slot - to leave as it is
TICK_DISPATCH_FREQUENCY_PERCENT = 10


class Oracle(RedisBCAggregator):
    """Class that defines the behaviour of an "oracle" aggregator."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_finished = False
        self.asset_strategy = {}

    def on_market_slot(self, market_info):
        """Place a bid or an offer whenever a new market is created."""
        if self.is_finished is True:
            return
        self.post_bid_offer()        
        self.build_strategies(market_info)


    def on_tick(self, tick_info):
        """Place a bid or an offer each 10% of the market slot progression."""
        rate_index = int(float(tick_info["slot_completion"].strip("%")) /
                         TICK_DISPATCH_FREQUENCY_PERCENT)
        self.post_bid_offer(rate_index)

    def build_strategies(self, market_info):
        """
        Assign a simple strategy to each asset in the form of an array of length 10,
        ranging between Feed-in Tariff and Market Maker rates.
        """
        fit_rate = market_info["feed_in_tariff_rate"]
        market_maker_rate = market_info["market_maker_rate"]
        med_price = (market_maker_rate - fit_rate) / 2 + fit_rate

        for area_uuid, area_dict in self.latest_grid_tree_flat.items():
            if "asset_info" not in area_dict or area_dict["asset_info"] is None:
                continue
            self.asset_strategy[area_uuid] = {}
            self.asset_strategy[area_uuid]["asset_name"] = area_dict["area_name"]
            self.asset_strategy[area_uuid][
                "fee_to_market_maker"
            ] = self.calculate_grid_fee(
                area_uuid,
                self.get_uuid_from_area_name("Market Maker"),
                "current_market_fee",
            )

            # Consumption strategy
            if "energy_requirement_kWh" in area_dict["asset_info"]:
                load_strategy = []
                for tick in range(0, TICK_DISPATCH_FREQUENCY_PERCENT):
                    if tick < TICK_DISPATCH_FREQUENCY_PERCENT - 2:
                        buy_rate = (fit_rate -
                                    self.asset_strategy[area_uuid]["fee_to_market_maker"] +
                                    (market_maker_rate +
                                     2 * self.asset_strategy[area_uuid]["fee_to_market_maker"] -
                                     fit_rate) * (tick / TICK_DISPATCH_FREQUENCY_PERCENT)
                                    )
                        load_strategy.append(buy_rate)
                    else:
                        buy_rate = (market_maker_rate +
                                    self.asset_strategy[area_uuid]["fee_to_market_maker"])
                        load_strategy.append(buy_rate)
                self.asset_strategy[area_uuid]["buy_rates"] = load_strategy

            # Generation strategy
            if "available_energy_kWh" in area_dict["asset_info"]:
                gen_strategy = []
                for tick in range(0, TICK_DISPATCH_FREQUENCY_PERCENT):
                    if tick < TICK_DISPATCH_FREQUENCY_PERCENT - 2:
                        sell_rate = (market_maker_rate +
                                     self.asset_strategy[area_uuid]["fee_to_market_maker"] -
                                     (market_maker_rate +
                                      2 * self.asset_strategy[area_uuid]["fee_to_market_maker"] -
                                      fit_rate) * (tick / TICK_DISPATCH_FREQUENCY_PERCENT)
                                     )
                        gen_strategy.append(max(0, sell_rate))
                    else:
                        sell_rate = fit_rate - (
                            self.asset_strategy[area_uuid]["fee_to_market_maker"])
                        gen_strategy.append(max(0, sell_rate))
                self.asset_strategy[area_uuid]["sell_rates"] = gen_strategy

            # Storage strategy
            if "used_storage" in area_dict["asset_info"]:
                batt_buy_strategy = []
                batt_sell_strategy = []
                for tick in range(0, TICK_DISPATCH_FREQUENCY_PERCENT):
                    buy_rate = (fit_rate -
                                self.asset_strategy[area_uuid]["fee_to_market_maker"] +
                                (med_price -
                                 (fit_rate -
                                  self.asset_strategy[area_uuid]["fee_to_market_maker"]
                                  )
                                 ) * (tick / TICK_DISPATCH_FREQUENCY_PERCENT)
                                )
                    batt_buy_strategy.append(buy_rate)
                    sell_rate = (market_maker_rate +
                                 self.asset_strategy[area_uuid]["fee_to_market_maker"] -
                                 (market_maker_rate +
                                  self.asset_strategy[area_uuid]["fee_to_market_maker"] -
                                  med_price) * (tick / TICK_DISPATCH_FREQUENCY_PERCENT)
                                 )
                    batt_sell_strategy.append(sell_rate)
                self.asset_strategy[area_uuid]["buy_rates"] = batt_buy_strategy
                self.asset_strategy[area_uuid]["sell_rates"] = batt_sell_strategy

    def post_bid_offer(self, rate_index=0):
        """Post a bid or an offer to the exchange."""
        for area_uuid, area_dict in self.latest_grid_tree_flat.items():
            asset_info = area_dict.get("asset_info")
            if not asset_info:
                continue

            # Consumption assets
            required_energy = asset_info.get("energy_requirement_kWh")
            if required_energy:
                rate = self.asset_strategy[area_uuid]["buy_rates"][rate_index]
                self.add_to_batch_commands.bid_energy_rate(
                    asset_uuid=area_uuid, rate=rate, energy=required_energy
                )

            # Generation assets
            available_energy = asset_info.get("available_energy_kWh")
            if available_energy:
                rate = self.asset_strategy[area_uuid]["sell_rates"][rate_index]
                self.add_to_batch_commands.offer_energy_rate(
                    asset_uuid=area_uuid, rate=rate, energy=available_energy
                )

            # Storage assets
            buy_energy = asset_info.get("energy_to_buy")
            if buy_energy:
                buy_rate = self.asset_strategy[area_uuid]["buy_rates"][rate_index]
                self.add_to_batch_commands.bid_energy_rate(
                    asset_uuid=area_uuid, rate=buy_rate, energy=buy_energy
                )

            sell_energy = asset_info.get("energy_to_sell")
            if sell_energy:
                sell_rate = self.asset_strategy[area_uuid]["sell_rates"][rate_index]
                self.add_to_batch_commands.offer_energy_rate(
                    asset_uuid=area_uuid, rate=sell_rate, energy=sell_energy
                )

            self.execute_batch_commands()

    def on_event_or_response(self, message):
        pass

    def on_finish(self, finish_info):
        self.is_finished = True


aggregator = Oracle(aggregator_name=ORACLE_NAME)
asset_args = {"autoregister": True, "pubsub_thread": aggregator.pubsub}


def register_asset_list(asset_names: List, asset_params: Dict, asset_uuid_map: Dict) -> Dict:
    """Register the provided list of assets with the aggregator."""
    for asset_name in asset_names:
        print("Registered asset:", asset_name)
        asset_params["area_id"] = asset_name
        asset = RedisAssetClient(**asset_params)
        print(asset)
        asset_uuid_map[asset.area_uuid] = asset.area_id
        asset.select_aggregator(aggregator.aggregator_uuid)
        market = b4p.Markets.new(asset.area_id, 'admin')
        print(market)
    return asset_uuid_map





print()
print("Registering assets ...")
asset_uuid_mapping = {}
asset_uuid_mapping = register_asset_list(LOAD_NAMES + PV_NAMES + STORAGE_NAMES,
                                         asset_args, asset_uuid_mapping)
print()
print("Summary of assets registered:")
print()
print(asset_uuid_mapping)

# loop to allow persistence
while not aggregator.is_finished:
    sleep(0.5)
