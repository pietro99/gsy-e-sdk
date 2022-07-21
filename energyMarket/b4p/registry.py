from . import p
class Registry():

    def __init__(self):
        from . import Accounts
        self.registry = p.MarketRegistry.deploy({"from": Accounts["admin"]})
        print(self.registry)


    def __str__(self):
        return self.registry.__str__()

    def __repr__(self):
        return self.registry.__repr__()

