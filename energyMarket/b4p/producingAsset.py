from . import p, EURS
class ProducingAssets():
    def __init__(self):
        self.producingAssetContract = p.ProducingAsset
        self.produducingAssets = {}

    def new(self,assetName, accountName, market2):
        from . import Markets, Accounts, Registry

        market = Markets[market2]
        account = Accounts[accountName]
        pa = self.producingAssetContract.deploy(market, Registry, {"from": account})
        EURS.transfer(pa, 1000, {"from":EURS})

        self.produducingAssets[assetName] = ProducingAsset(pa, account)
        return self.produducingAssets[assetName]

    def __getitem__(self, name):
        if name in self.produducingAssets:
            return self.produducingAssets[name]
        return False




class ProducingAsset():
    def __init__(self, asset, account):
        self.asset = asset
        self.owner = account

    def __str__(self):
        return self.asset.__str__()

    def __repr__(self):
        return self.asset.__repr__()

    def createOffer(self, price, amount):
        tx = self.asset.createOffer(price, amount, {"from": self.owner})
        tx.wait(1)
    
    def balanceEURS(self):
        return EURS.balanceOf(self.asset)

    def balanceEnergyToken(self):
        from . import EnergyToken
        return EnergyToken.balanceOf(self.asset)



