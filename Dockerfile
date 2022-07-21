FROM python:3.10

ADD . /app

WORKDIR /app
# TODO remove in the frame of D3ASIM-3093:
RUN pip install -U pip==20.2.4
RUN pip install -e .
RUN pip install -e gsy-framework
WORKDIR /app/energyMarket
RUN pip install -e .
RUN brownie pm install OpenZeppelin/openzeppelin-contracts@4.5.0
WORKDIR /app
ENTRYPOINT ["gsy-e-sdk"]