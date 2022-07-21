import uuid
from brownie import config, network, project, Contract
import sys, os


has_started = False

def init():
    global has_started
    global p
    global zero_address
    global url
    global EURS

    has_started = True

    project_path = os.path.dirname(os.path.realpath(__file__))+"/b4p-contracts"
    p = project.load(project_path)
    p.load_config()
    network.connect('mainnet-fork')
    

    EURS = Contract.from_explorer(config["networks"][network.show_active()].get("eurs"))
    zero_address = "0x0000000000000000000000000000000000000000"
    url = "https://exampleURL.com"
    from .accounts import Accounts
    from .energyToken import EnergyToken
    from .market import Markets
    from .producingAsset import ProducingAssets
    from .consumingAsset import ConsumingAssets

    from .registry import Registry

    globals()["Accounts"] = Accounts()
    globals()["EnergyToken"] = EnergyToken()
    globals()["Registry"] = Registry()
    globals()["Markets"] = Markets()
    globals()["ProducingAssets"] = ProducingAssets()
    globals()["ConsumingAssets"] = ConsumingAssets()

    

def started():
    return has_started


class BC4PBlockchainInterface:
    def __init__(self, market_id, simulation_id=None):
        import b4p
        self.market_id = market_id
        self.simulation_id = simulation_id
        b4p.Markets.new(market_id, "admin")
        print(f"new market created with id: {market_id}")


    def create_new_offer(self, energy, price, seller):
        import b4p

        if not b4p.Accounts[seller+"_account"]:
            print(f"new account created: {seller}_account")
            b4p.Accounts.new(seller+"_account")
        if not b4p.ProducingAssets[seller]:
            print(f"new producing asset created: {seller} for market: {self.market_id}")
            b4p.ProducingAssets.new(seller, seller+"_account", self.market_id)
        return str(uuid.uuid4())

    def cancel_offer(self, offer):
        pass

    def change_offer(self, offer, original_offer, residual_offer):
        pass

    def handle_blockchain_trade_event(self, offer, buyer, original_offer, residual_offer):
        return str(uuid.uuid4()), residual_offer

    def track_trade_event(self, time_slot, trade):
        pass

    def bc_listener(self):
        pass