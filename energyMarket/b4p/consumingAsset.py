from . import p, EURS

class ConsumingAssets():
    def __init__(self):
        self.consumingAssetContract = p.ConsumingAsset
        self.consumingAssets = {}

    def new(self,assetName, accountName, market1):
        from . import Markets, Registry, Accounts
        market = Markets[market1]
        account = Accounts[accountName]
        ca = self.consumingAssetContract.deploy(market, Registry, {"from": account})
        EURS.transfer(ca, 1000, {"from":EURS})
        self.consumingAssets[assetName] = ConsumingAsset(ca,account)
        return self.consumingAssets[assetName]

    def __getitem__(self, name):
        if name in self.consumingAssets:
            return self.consumingAssets[name]
        return False


class ConsumingAsset():
    def __init__(self, asset, owner):
        self.asset = asset
        EURS.transfer(self.asset, 1000, {"from": EURS})
        self.owner = owner

    def __str__(self):
        return self.asset.__str__()

    def __repr__(self):
        return self.asset.__repr__()
        
    def createBid(self, price, amount):
        tx = self.asset.createBid(price, amount, {"from":self.owner})
        tx.wait(1)
    
    def balanceEURS(self):
        return EURS.balanceOf(self.asset)

    def balanceEnergyToken(self):
        from . import EnergyToken
        return EnergyToken.balanceOf(self.asset)

