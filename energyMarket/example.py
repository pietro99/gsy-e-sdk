import b4p 
if not b4p.started():
    b4p.init()

b4p.Accounts.new("energy provider")
b4p.Accounts.new("energy consumer")
b4p.Accounts.new("neighborhood operator")

house1 = b4p.Markets.new("house1","energy provider")
house2 = b4p.Markets.new("house2","energy consumer")


account = b4p.Accounts["energy provider"]
neighborhood = b4p.Markets.new("neighborhood","neighborhood operator")
solar_panel = b4p.ProducingAssets.new("solar panel", "energy provider", "house1")
load = b4p.ConsumingAssets.new("load", "energy consumer", "house2")

house1.setConnections("neighborhood")
house2.setConnections("neighborhood")

solar_panel.createOffer(7, 10)
load.createBid(10, 10)
house2.forwardBid(0)
house1.forwardOffer(0)


print(solar_panel.balanceEURS())
print(load.balanceEURS())

print(solar_panel.balanceEnergyToken())
print(load.balanceEnergyToken())


