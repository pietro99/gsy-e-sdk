# b4p package

## setup

clone this repository with its submodules by calling

```
git clone --recurse-submodules https://github.com BC4P/energyMarket.git
```  
Next, locate the .env file inside [b4p/b4p-contracts/.env](https://github.com/BC4P/b4p-contracts/blob/master/.env) and fill in the api keys for [infura](https://infura.io) and [etherscan](https://etherscan.io/). The api keys will be used to connect to the blockchain through an infura node and pull down external contracts through the etherscan API. 

Only when the api keys are in the .env file you can go to the root directory and install the package by running.

```
cd energyMarket
pip install .
```

:warning:if the .env values are changed the package needs to be reinstalled with the command above:warning:

## use

see the [tutorial notebook](tutorial.ipynb) to get familari with the main functionalities of the package

