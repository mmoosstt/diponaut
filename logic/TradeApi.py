import numpy
import os

import traceback
import xml.etree.ElementTree
import logic.TradeServerTime as time
import binance.client
from logic.TradeGlobals import GloVar

import logic.TradeStateMachine.Transitions as Transitions
import logic.TradeStateMachine.StateMachines as StateMachines
import logic.TradeStateMachine.States as States


if 0:
    States.BuyOrder
    States.SellOrder
    States.Start

    Transitions.bought
    Transitions.sold
    Transitions.coins_to_sell


class ApiData(object):

    def __init__(self):
        self.trades_count = 0
        self.trades_time = time.time()
        self.value_mean_quantity = 0
        self.value_min = 0
        self.value_max = 0
        self.value_open = 0
        self.value_close = 0
        self.quantity = 0


class BinanceClient(object):

    def __init__(self, file_path="./data/config.xml"):

        _e = xml.etree.ElementTree.parse(file_path)
        _key = _e.find("./binance/key").text
        _secret = _e.find("./binance/secret").text

        self.binance_api = binance.client.Client(_key, _secret)

        # synchronise time module
        # and synchronise time stamp client with time stamp server

        binance.client.time = time
        binance.client.time.Timer.synchronise(self.binance_api)


class Api(object):

    def __init__(self, file_path):

        # search for config file by stepping up in the folder structure
        _isfile = os.path.isfile(file_path)
        for _x in range(5):

            _isfile = os.path.isfile(file_path)

            if _isfile:
                break
            else:
                file_path = "../{0}".format(file_path)

        self.binance_api = BinanceClient(file_path).binance_api

    def getTradeData(self, startTime, endTime):

        try:
            _trades = self.binance_api.get_aggregate_trades(
                symbol=GloVar.get("trade_symbol"), startTime=startTime, endTime=int(time.time() * 1000))
        except:
            _trades = []
            traceback.print_exc()

        names = {"id": "a", "price": "p", "quantity": "q", "time": "T"}

        if _trades != []:

            _id = []
            _price = []
            _quantity = []
            _time = []
            for _trade in _trades:

                _id.append(_trade[names['id']])
                _price.append(_trade[names['price']])
                _quantity.append(_trade[names['quantity']])
                _time.append(_trade[names['time']] / 1000)

            _price = numpy.array(_price, numpy.double)
            _quantity = numpy.array(_quantity, numpy.double)

            data = ApiData()
            data.value_open = _price[0]
            data.value_close = _price[-1:]
            data.value_mean_quantity = numpy.sum(_price * _quantity) / numpy.sum(_quantity)
            data.value_max = numpy.max(_price)
            data.value_min = numpy.min(_price)
            data.quantity = numpy.sum(_quantity)
            data.trades_count = len(_price)
            data.trades_time = (min(_time) + max(_time)) / 2.

            return data

        return None

    def create_buy_order(self):

        _ret = self.binance_api.create_order(
            symbol=GloVar.get("trade_symbol"),
            side=binance.client.Client.SIDE_BUY,
            type=binance.client.Client.ORDER_TYPE_MARKET,
            quantity=GloVar.get("trade_quantity"))

        return _ret

    def create_sell_order(self):

        _ret = self.binance_api.create_order(
            symbol=GloVar.get("trade_symbol"),
            side=binance.client.Client.SIDE_SELL,
            type=binance.client.Client.ORDER_TYPE_MARKET,
            quantity=GloVar.get("trade_quantity"))

        return _ret

    def account_limit(self):

        _cnt_buy = None
        _cnt_sell = None

        _symbol = GloVar.get("trade_symbol")
        _asset_name1 = _symbol[:3]
        _asset_name2 = _symbol[3:]

        _t_server = self.binance_api.get_server_time()["serverTime"]
        _t_local = int(time.time() * 1000)
        _t_delta = int(GloVar.get("trade_sample_time") * 1000)

        _trade_data = self.getTradeData(_t_local - _t_delta, _t_local)
        if _trade_data:

            # _price_asset1 =
            _price = _trade_data.value_mean_quantity

            _asset1 = self.binance_api.get_asset_balance(asset=_asset_name1)
            _asset2 = self.binance_api.get_asset_balance(asset=_asset_name2)

            if _asset1 and _asset2:
                _cnt_sell = float(_asset1['free'])  # [1]
                _cnt_buy = float(_asset2['free']) / _price

                _value_sell = float(_asset1['free']) * _price
                _value_buy = float(_asset2['free'])

        return _cnt_buy, _cnt_sell

if __name__ == "__main__":
    #import time

    api = Api("../config/config.xml")

    for x in range(10):
        time.Timer.synchronise(api.binance_api)

        api.account_limit()

    #address = api.binance_api.get_asset_balance(asset='XVG')
    # print(address)

    #address = api.binance_api.get_asset_balance(asset='ETH')
    # print(address)

    #print(api.getTradeData(int(time.time() * 1000 - 10000), endTime=int(time.time() * 1000)))
    # api.create_buy_order()
    # api.create_sell_order()
