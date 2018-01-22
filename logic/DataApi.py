import time
import h5py
import numpy as np
import os
import sys
from binance.client import Client
import scipy
import scipy.signal
import matplotlib.pyplot as plt


class BinanceClient(object):

    api = None

    def __init__(self, file_path="../data/BinanceApi.hdf5"):

        if __class__.api == None:
            _f = h5py.File(file_path, 'r')
            self.key = _f['key_storage'].attrs['key']
            self.key_secret = _f['key_storage'].attrs['key_secret']
            _f.close()

            __class__.api = Client(self.key,  self.key_secret)


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


class TradesApi(object):

    client = BinanceClient()

    @staticmethod
    def getTradeData(startTime, endTime, symbol='BNBBTC'):

        _trades = __class__.client.api.get_aggregate_trades(
            symbol='BNBBTC', startTime=startTime, endTime=endTime)
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

            _price = np.array(_price, np.double)
            _quantity = np.array(_quantity, np.double)

            data = TradeData()
            data.value_open = _price[0]
            data.value_close = _price[-1:]
            data.value_mean_quantity = np.sum(
                _price * _quantity) / np.sum(_quantity)
            data.value_max = np.max(_price)
            data.value_min = np.min(_price)
            data.quantity = np.sum(_quantity)
            data.trades_count = len(_price)
            data.trades_time = (min(_time) + max(_time)) / 2.

            return data
        else:
            return []


class TradesLogger(object):

    def __init__(self, symbol='BNBBTC', time_delta=60, storages_path="../data"):

        self.time_delta = time_delta
        self.time_last_update = 0
        self.symbol = symbol

        _data = TradeData()

        if _data != []:

            self.ring_size = int(60 * 60 * 24 / time_delta)
            self.ring_data_filepath = "{0}/{1}-{2}s-[{3}].hdf".format(
                storages_path, symbol, time_delta, self.ring_size)
            self.ring_pos = int(0)
            self.ring_trades_count = np.array(
                [_data.trades_count] * self.ring_size, dtype=np.int)
            self.ring_trades_time = np.array(
                [_data.trades_time] * self.ring_size, dtype=np.double)
            self.ring_value_mean_quantity = np.array(
                [_data.value_mean_quantity] * self.ring_size, dtype=np.double)
            self.ring_value_max = np.array(
                [_data.value_max] * self.ring_size, dtype=np.double)
            self.ring_value_min = np.array(
                [_data.value_min] * self.ring_size, dtype=np.double)
            self.ring_value_close = np.array(
                [_data.value_open] * self.ring_size, dtype=np.double)
            self.ring_value_open = np.array(
                [_data.value_close] * self.ring_size, dtype=np.double)
            self.ring_quantity = np.array(
                [_data.quantity] * self.ring_size, dtype=np.double)

            if not os.path.isfile(self.ring_data_filepath):
                self.save_storage(self.ring_data_filepath)

            self.load_storage(self.ring_data_filepath)

    def load_storage(self, file_path):
        _f = h5py.File(file_path, 'r')
        self.ring_trades_count = np.array(
            _f['ring_trades_count'], dtype=np.int)
        self.ring_trades_time = np.array(
            _f['ring_trades_time'], dtype=np.double)
        self.ring_value_mean_quantity = np.array(
            _f['ring_value_mean_quantity'], dtype=np.double)
        self.ring_value_max = np.array(_f['ring_value_max'], dtype=np.double)
        self.ring_value_min = np.array(_f['ring_value_min'], dtype=np.double)
        self.ring_value_close = np.array(
            _f['ring_value_close'], dtype=np.double)
        self.ring_value_open = np.array(_f['ring_value_open'], dtype=np.double)
        self.ring_quantity = np.array(_f['ring_quantity'], dtype=np.double)
        self.ring_pos = int(_f['ring_pos'].value)
        _f.close()

    def save_storage(self, file_path):
        _f = h5py.File(file_path, 'w')
        _f.create_dataset('ring_trades_count', data=self.ring_trades_count)
        _f.create_dataset('ring_trades_time', data=self.ring_trades_time)
        _f.create_dataset(
            'ring_value_mean_quantity', data=self.ring_value_mean_quantity)
        _f.create_dataset('ring_value_max', data=self.ring_value_max)
        _f.create_dataset('ring_value_min', data=self.ring_value_min)
        _f.create_dataset('ring_value_close', data=self.ring_value_close)
        _f.create_dataset('ring_value_open', data=self.ring_value_open)
        _f.create_dataset('ring_quantity', data=self.ring_quantity)
        _f.create_dataset('ring_pos', data=self.ring_pos)
        _f.close()

    def update_ring(self):

        _endTime = int(time.time() * 1000)

        # compensation of calculation time
        if self.time_last_update <= 0:
            _errTime = 0
        else:
            # limited to 10 seconds
            _errTime = max(-10000, min(10000, (_endTime -
                                               self.time_last_update) - self.time_delta * 1e3))

        _startTime = int(_endTime - _errTime - self.time_delta * 1e3)

        _trade = TradesApi.getTradeData(_startTime, _endTime, self.symbol)

        self.time_last_update = _endTime

        self.ring_trades_count[self.ring_pos] = _trade.trades_count
        self.ring_trades_time[self.ring_pos] = _trade.trades_time
        self.ring_value_close[self.ring_pos] = _trade.value_close
        self.ring_value_max[self.ring_pos] = _trade.value_max
        self.ring_value_min[self.ring_pos] = _trade.value_min
        self.ring_value_mean_quantity[
            self.ring_pos] = _trade.value_mean_quantity
        self.ring_value_open[self.ring_pos] = _trade.value_open
        self.ring_quantity[self.ring_pos] = _trade.quantity

        self.ring_pos = self.ring_pos + 1
        if self.ring_pos == self.ring_size:
            self.ring_pos = 0

        self.save_storage(self.ring_data_filepath)


class TradesPrediction(object):

    Trades = TradesLogger

    def __init__(self, time_delta=10):
        self.ring_size = int(60 * 60 * 24 / time_delta)
        self.trades_raw = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_median = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_direction = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_err = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_time = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_err_ana = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_buy = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_sell = np.array([0] * self.ring_size, dtype=np.double)

    def update(self, source):

        _dummy = np.concatenate((source.ring_trades_time[source.ring_pos:],
                                 source.ring_trades_time[:source.ring_pos]))

        np.copyto(self.trades_time, _dummy)

        _dummy = np.concatenate((source.ring_value_mean_quantity[source.ring_pos:],
                                 source.ring_value_mean_quantity[:source.ring_pos]))

        np.copyto(self.trades_raw, _dummy)

        # calc _trades_median
        _filt_w = 200 * 6
        _d1 = np.flip(self.trades_raw[-1 * _filt_w:], 0)
        _d1 = np.concatenate((self.trades_raw, _d1), 0)
        _d1 = scipy.signal.medfilt(_d1, _filt_w + 1)
        _trades_median = _d1[:-1 * _filt_w]
        np.copyto(self.trades_median, _trades_median)

        # calc median deviation
        b, a = scipy.signal.butter(2, 0.075)
        _trades_err = (self.trades_raw - self.trades_median)
        _trades_err = scipy.signal.filtfilt(b, a, _trades_err, padlen=150)
        _trades_err_diff = scipy.diff(_trades_err)
        np.copyto(self.trades_err, _trades_err)

        # predic raising or fallin global tendencies
        b, a = scipy.signal.butter(2, 0.075)
        _trades_median_diff = scipy.diff(_trades_median)
        _trades_median_diff = scipy.signal.filtfilt(b, a, _trades_median_diff, padlen=150)

        # predicted trade level, zc zero crossings
        _trades_err_diff_zc = (_trades_err_diff[:-1] * _trades_err_diff[1:]) < 0
        _trades_ana1 = _trades_err_diff_zc * self.trades_err[1:-1]

        np.copyto(self.trades_err_ana[2:], _trades_ana1)

        _trades_level_sell = self.trades_err_ana[scipy.where(self.trades_err_ana > 0)]
        _len = len(_trades_level_sell)
        _current_trade_level_sell = (np.mean(_trades_level_sell[:int(_len / 2)]) + np.mean(_trades_level_sell[int(_len / 2):]) * 3.) / 4.
        _trades_sell = (_trades_err > 1.5 * _current_trade_level_sell) * 1.5 * _current_trade_level_sell
        np.copyto(self.trades_sell, _trades_sell)

        _trades_level_buy = self.trades_err_ana[scipy.where(self.trades_err_ana < 0)]
        _len = len(_trades_level_buy)
        _current_trade_level_buy = (np.mean(_trades_level_buy[:int(_len / 2)]) + np.mean(_trades_level_buy[int(_len / 2):]) * 3.) / 4.
        _trades_buy = (_trades_err < -1.5 * _current_trade_level_sell) * -1.5 * _current_trade_level_sell
        np.copyto(self.trades_buy, _trades_buy)

        buy_event = (_trades_err < -1.5 * _current_trade_level_sell)[-1:][0]
        sell_event = (_trades_err > 1.5 * _current_trade_level_sell)[-1:][0]
        price = source.ring_value_mean_quantity[source.ring_pos]
        zc = True in _trades_err_diff_zc[-10:]

        TradingStates.update(price, buy_event, sell_event, zc)


class TradingStates(object):

    state = "_sell"
    price_week = 0
    price_strong = 0
    zc_cnt = 0

    @staticmethod
    def update(price=0, buy_limit=False, sell_limit=False, zc=False):

        if zc:
            __class__.zc_cnt = min(3, __class__.zc_cnt + 1)

        else:
            __class__.zc_cnt = max(0, __class__.zc_cnt - 1)

        zc = False
        if __class__.zc_cnt >= 3:
            zc = True

        if __class__.state.find("_sell") > -1 and buy_limit == True:
            __class__.state = "week_buy"
            __class__.price_week = price
            print(__class__.state, time.ctime(time.time()), price)

        elif __class__.state == "week_buy" and zc == True:
            __class__.state = "stro_buy"
            __class__.price_strong = price
            print(__class__.state, time.ctime(time.time()), price)

        elif __class__.state == "week_sell" and zc == True:
            __class__.state = "stro_sell"
            __class__.price_week = price
            print(__class__.state, time.ctime(time.time()), price)

        elif __class__.state.find('_buy') > -1 and sell_limit == True:
            __class__.state = "week_sell"
            __class__.price_week = price
            print(__class__.state, time.ctime(time.time()), price)

        elif zc == True:
            __class__.price_week = price
            print(__class__.state, time.ctime(time.time()), price, "<- Risk")

            print(__class__.state, time.ctime(time.time()), price)

if __name__ == "__main__":
    fig, (ax1) = plt.subplots(1, sharey=False)

    _logger = TradesLogger(time_delta=10, symbol="TRXETH")
    _predict = TradesPrediction(time_delta=10)
    _logger.update_ring()
    _predict.update(_logger)
