from collections import Counter
from . import p, zero_address, EURS

class Markets():

    def __init__(self):
        self.marketContract = p.Market
        self.markets = {}
        self.markets[ zero_address] =  zero_address

    def new(self, nameMarket, nameAccount, fee=0, connection1= zero_address, connection2= zero_address):
        from . import EnergyToken, Registry, Accounts
        #TODO: check if account exists before deploying the market
        account =  Accounts[nameAccount]
        market = self.marketContract.deploy( EURS, EnergyToken, connection1, connection2,  Registry, fee, {"from": account})
        self.markets[nameMarket] = Market(market, account)
        return self.markets[nameMarket]

    def __getitem__(self, name):
        if name in self.markets:
            return self.markets[name]
        return False

class Market():
    def __init__(self, market, account):
        self.market = market
        EURS.transfer(self.market, 1000, {"from":  EURS})
        self.owner = account

    def __str__(self):
        return self.market.__str__()

    def __repr__(self):
        return self.market.__repr__()

    def setConnections(self, nameMarket1= zero_address, nameMarket2= zero_address):
        import b4p

        tx = self.market.setMarkets(b4p.Markets[nameMarket1], b4p.Markets[nameMarket2], {"from": self.owner})
        tx.wait(1)

    def forwardOffer(self, id):
        tx = self.market.forwardOffer(id, {"from": self.owner})
        tx.wait(1)

    def forwardBid(self, id):
        tx = self.market.forwardBid(id, {"from": self.owner})
        tx.wait(1)
        print(tx.call_trace())

    def balanceEURS(self):
        return  EURS.balanceOf(self.market)

    def balanceEnergyToken(self):
        from . import EnergyToken
        return EnergyToken.balanceOf(self.market)

    


        


