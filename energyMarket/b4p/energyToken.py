from . import url, p
class EnergyToken():
        def __init__(self):
            from . import Accounts
            self.energyToken = p.EnergyToken.deploy(url, {"from": Accounts["admin"]})

        def __str__(self):
            return self.energyToken.__str__()

        def __repr__(self):
            return self.energyToken.__repr__()

        def balanceOf(self, address):
            return self.energyToken.balanceOf(address, 1)