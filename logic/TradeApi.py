import numpy
import binance.client
import traceback
import xml.etree.ElementTree as et
import time
import os
import h5py


class TradeData(object):

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

        _e = et.parse(file_path)
        _key = _e.find("//binance/key").text
        _secret = _e.find("//binance/secret").text
        self.binance_api = binance.client.Client(_key, _secret)


class TradeApi(object):

    def __init__(self, symbol="TRXETH", time_delta=10, file_path_data="", file_path_config="./data/config.xml"):
        self.binance_api = BinanceClient(file_path_config).binance_api
        self.symbol = symbol
        self.time_delta = time_delta

    def getTradeData(self, startTime, endTime):

        try:
            _trades = self.binance_api.get_aggregate_trades(
                symbol=self.symbol, startTime=startTime, endTime=endTime)
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

            data = TradeData()
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

    def create_buy_order(self, quantity=100):

        _ret = self.binance_api.create_order(
            symbol=self.symbol,
            side=binance.client.Client.SIDE_BUY,
            type=binance.client.Client.ORDER_TYPE_MARKET,
            quantity=quantity)

        print(_ret)

    def create_sell_order(self, quantity=100):

        _ret = self.binance_api.create_order(
            symbol=self.symbol,
            side=binance.client.Client.SIDE_SELL,
            type=binance.client.Client.ORDER_TYPE_MARKET,
            quantity=quantity)

        print(_ret)
