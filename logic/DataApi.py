import time
import h5py
import numpy as np
import os
import sys
from binance.client import Client
import scipy
import scipy.signal
import matplotlib.pyplot as plt
import traceback


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
    def getTradeData(startTime, endTime, symbol='TRXETH'):

        try:
            _trades = __class__.client.api.get_aggregate_trades(
                symbol=symbol, startTime=startTime, endTime=endTime)
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
            return None

    @staticmethod
    def create_buy_order(symbols='TRXETH', quantity=100):

        _ret = __class__.client.api.create_order(
            symbol=symbols,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity)

        print(_ret)

    @staticmethod
    def create_sell_order(symbols="TRXETH", quantity=100):

        _ret = __class__.client.api.create_order(
            symbol=symbols,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity)

        print(_ret)


class TradesLogger(object):

    def __init__(self, symbol='TRXETH', time_delta=10, storages_path="../data"):

        self.time_delta = time_delta
        self.time_last_update = 0
        self.symbol = symbol

        _data = TradeData()

        if _data != []:

            self.ring_size = int(60 * 60 * 24 / time_delta)
            self.ring_data_filepath = "{0}/{1}-{2}s-{3}.hdf".format(
                storages_path, symbol, time_delta, "logger")
            self.ring_pos = int(0)
            self.ring_trades_count = np.array([_data.trades_count] * self.ring_size, dtype=np.int)
            self.ring_trades_time = np.array([_data.trades_time] * self.ring_size, dtype=np.double)
            self.ring_value_mean_quantity = np.array([_data.value_mean_quantity] * self.ring_size, dtype=np.double)
            self.ring_value_max = np.array([_data.value_max] * self.ring_size, dtype=np.double)
            self.ring_value_min = np.array([_data.value_min] * self.ring_size, dtype=np.double)
            self.ring_value_close = np.array([_data.value_open] * self.ring_size, dtype=np.double)
            self.ring_value_open = np.array([_data.value_close] * self.ring_size, dtype=np.double)
            self.ring_quantity = np.array([_data.quantity] * self.ring_size, dtype=np.double)

            if not os.path.isfile(self.ring_data_filepath):
                self.save_storage(self.ring_data_filepath)

            self.load_storage(self.ring_data_filepath)

    def load_storage(self, file_path):
        _f = h5py.File(file_path, 'r')
        self.ring_trades_count = np.array(_f['ring_trades_count'], dtype=np.int)
        self.ring_trades_time = np.array(_f['ring_trades_time'], dtype=np.double)
        self.ring_value_mean_quantity = np.array(_f['ring_value_mean_quantity'], dtype=np.double)
        self.ring_value_max = np.array(_f['ring_value_max'], dtype=np.double)
        self.ring_value_min = np.array(_f['ring_value_min'], dtype=np.double)
        self.ring_value_close = np.array(_f['ring_value_close'], dtype=np.double)
        self.ring_value_open = np.array(_f['ring_value_open'], dtype=np.double)
        self.ring_quantity = np.array(_f['ring_quantity'], dtype=np.double)
        self.ring_pos = int(_f['ring_pos'].value)
        _f.close()

    def save_storage(self, file_path):
        _f = h5py.File(file_path, 'w')
        _f.create_dataset('ring_trades_count', data=self.ring_trades_count)
        _f.create_dataset('ring_trades_time', data=self.ring_trades_time)
        _f.create_dataset('ring_value_mean_quantity', data=self.ring_value_mean_quantity)
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

        if _trade != None:
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

    def __init__(self,  symbol="TRXETH", time_delta=10, storages_path="../data"):
        self.states = TradingStates(symbol, time_delta, storages_path)
        self.time_delta = time_delta  # s
        self.ring_size = int(60 * 60 * 24 / time_delta)
        self.trades_time = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_err_ana = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_raw = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_median = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_filt1 = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_filt2 = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_err_diff_zc = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_filt2_diff = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_err = np.array([0] * self.ring_size, dtype=np.double)
        self.trades_buy = np.array([np.NaN] * self.ring_size, dtype=np.double)
        self.trades_sell = np.array([np.NaN] * self.ring_size, dtype=np.double)

        self.ring_data_filepath = "{0}/{1}-{2}s-{3}.hdf".format(
            storages_path, symbol, time_delta, "prediction")

        if not os.path.isfile(self.ring_data_filepath):
            self.save_storage(self.ring_data_filepath)

        self.load_storage(self.ring_data_filepath)

    def load_storage(self, file_path):
        _f = h5py.File(file_path, 'r')
        self.trades_time = np.array(_f['trades_time'], dtype=np.double)
        self.trades_median = np.array(_f['trades_median'], dtype=np.double)
        self.trades_filt1 = np.array(_f['trades_filt1'], dtype=np.double)
        self.trades_filt2 = np.array(_f['trades_filt2'], dtype=np.double)
        self.trades_err = np.array(_f['trades_err'], dtype=np.double)
        self.trades_buy = np.array(_f['trades_buy'], dtype=np.double)
        self.trades_sell = np.array(_f['trades_sell'], dtype=np.double)
        _f.close()

    def save_storage(self, file_path):
        _f = h5py.File(file_path, 'w')
        _f.create_dataset('trades_time', data=self.trades_time)
        _f.create_dataset('trades_median', data=self.trades_median)
        _f.create_dataset('trades_filt1', data=self.trades_filt1)
        _f.create_dataset('trades_filt2', data=self.trades_filt2)
        _f.create_dataset('trades_err', data=self.trades_err)
        _f.create_dataset('trades_buy', data=self.trades_buy)
        _f.create_dataset('trades_sell', data=self.trades_sell)
        _f.close()

    def update(self, source):

        _dummy = np.concatenate((source.ring_trades_time[source.ring_pos:],
                                 source.ring_trades_time[:source.ring_pos]))

        np.copyto(self.trades_time, _dummy)

        _dummy = np.concatenate((source.ring_value_mean_quantity[source.ring_pos:],
                                 source.ring_value_mean_quantity[:source.ring_pos]))

        np.copyto(self.trades_raw, _dummy)

        _trades_trigger_factor = 1.0

        # predic raising or fallin global tendencies
        b, a = scipy.signal.butter(2, 0.01)
        _trades_filt1 = scipy.signal.filtfilt(b, a, (self.trades_raw, self.trades_time), axis=1)
        np.copyto(self.trades_filt1, _trades_filt1[0])

        # predic raising or fallin global tendencies
        b, a = scipy.signal.butter(2, 0.001)
        _trades_filt2 = scipy.signal.filtfilt(b, a, (self.trades_raw, self.trades_time), axis=1)
        np.copyto(self.trades_filt2, _trades_filt2[0])

        _trades_filt2_diff = scipy.diff((self.trades_filt2, self.trades_time), axis=1)[0]
        np.copyto(self.trades_filt2_diff[1:], _trades_filt2_diff)
        # calc median deviation
        _trades_err = (self.trades_filt1 - self.trades_filt2)
        np.copyto(self.trades_err, _trades_err)

        # steigung trades error
        _trades_err_diff = scipy.diff(_trades_err)

        # predicted trade level, zc zero crossings
        _trades_err_diff_zc = (_trades_err_diff[:-1] * _trades_err_diff[1:]) < 0.
        _trades_err_diff_zc_value = _trades_err_diff_zc * self.trades_err[1:-1]
        np.copyto(self.trades_err_diff_zc[2:], _trades_err_diff_zc_value)

        _int = -1 * int(1. * 60 * 60 / self.time_delta)

        _trade_level_sell = self.trades_err_diff_zc[scipy.where(self.trades_err_diff_zc > 0)]
        _trade_level_sell = np.mean(_trade_level_sell[_int:])

        np.copyto(self.trades_sell[:-1], self.trades_sell[1:])
        self.trades_sell[len(self.trades_sell) - 1] = _trade_level_sell

        _trade_level_buy = self.trades_err_diff_zc[scipy.where(self.trades_err_diff_zc < 0)]
        _trade_level_buy = np.mean(_trade_level_buy[_int:])

        np.copyto(self.trades_buy[:-1], self.trades_buy[1:])
        self.trades_buy[len(self.trades_buy) - 1] = _trade_level_buy

        def update_array(ring, event, price):

            if event:
                ring[len(self.trades_buy) - 1] = price
            else:
                ring[len(self.trades_buy) - 1] = np.NaN

        self.save_storage(self.ring_data_filepath)

        _event_price = source.ring_value_mean_quantity[source.ring_pos]
        _event_buy = _trades_err[-1:][0] < _trade_level_buy
        _event_sell = _trades_err[-1:][0] > _trade_level_sell
        _event_zc = True in _trades_err_diff_zc[-10:]
        _event_rising = (self.trades_filt2_diff[-1:][0]) >= 0
        _event_time = self.trades_time[-1:][0]

        self.states.update(_event_price, _event_time, _event_buy, _event_sell, _event_zc, _event_rising)


class TradingStates(object):

    def __init__(self, symbol="TRXETH", time_delta=10, storages_path="../data"):
        self.symbol = symbol
        self.state = "start"
        self.state_z = "start"
        self.zc_cnt = 0
        self.ring_size = int(60 * 60 * 24 / time_delta)
        self.events_buy = np.array([np.NaN] * self.ring_size, dtype=np.double)
        self.events_sell = np.array([np.NaN] * self.ring_size, dtype=np.double)
        self.events_zc = np.array([np.NaN] * self.ring_size, dtype=np.double)
        self.events_buy_time = np.array([np.NaN] * self.ring_size, dtype=np.double)
        self.events_sell_time = np.array([np.NaN] * self.ring_size, dtype=np.double)
        self.events_zc_time = np.array([np.NaN] * self.ring_size, dtype=np.double)

        self.ring_data_filepath = "{0}/{1}-{2}s-{3}.hdf".format(
            storages_path, symbol, time_delta, "events")

        if not os.path.isfile(self.ring_data_filepath):
            self.save_storage(self.ring_data_filepath)

        self.load_storage(self.ring_data_filepath)

    def load_storage(self, file_path):
        _f = h5py.File(file_path, 'r')
        self.events_buy = np.array(_f['events_buy'], dtype=np.double)
        self.events_buy_time = np.array(_f['events_buy_time'], dtype=np.double)
        self.events_sell = np.array(_f['events_sell'], dtype=np.double)
        self.events_sell_time = np.array(_f['events_sell_time'], dtype=np.double)
        self.events_zc = np.array(_f['events_zc'], dtype=np.double)
        self.events_zc_time = np.array(_f['events_zc_time'], dtype=np.double)
        _f.close()

    def save_storage(self, file_path):
        _f = h5py.File(file_path, 'w')
        _f.create_dataset('events_buy', data=self.events_buy)
        _f.create_dataset('events_buy_time', data=self.events_buy_time)
        _f.create_dataset('events_sell', data=self.events_sell)
        _f.create_dataset('events_sell_time', data=self.events_sell_time)
        _f.create_dataset('events_zc', data=self.events_zc)
        _f.create_dataset('events_zc_time', data=self.events_zc_time)
        _f.close()

    def update_event(self, events_arr, event, value):

        if event:
            np.copyto(events_arr[:-1], events_arr[1:])
            events_arr[len(events_arr) - 1] = value

        self.save_storage(self.ring_data_filepath)

    def update(self, price, time_event, buy_event=False, sell_event=False, zc_event=False, rising_event=False):

        if zc_event:
            self.zc_cnt = min(3, self.zc_cnt + 1)

        else:
            self.zc_cnt = max(0, self.zc_cnt - 1)

        zc_event = False
        if self.zc_cnt >= 3:
            zc_event = True
            self.update_event(self.events_zc_time, True, time_event)
            self.update_event(self.events_zc, True, price)
        if (
            (self.state == "start" or
             self.state == "stro_sell") and
                buy_event == True):

            self.state = "week_buy"
            self.price_week = price

        elif (self.state == "week_buy" and
              zc_event == True):
            self.state = "stro_buy"
            self.update_event(self.events_buy_time, True, time_event)
            self.update_event(self.events_buy, True, price)

            TradesApi.create_buy_order(self.symbol, 500)

        elif (self.state == "stro_buy" and
              sell_event == True):
            self.state = "week_sell"
            self.price_week = price

        elif (self.state == "week_sell" and
              zc_event == True):
            self.state = "stro_sell"
            self.update_event(self.events_sell_time, True, time_event)
            self.update_event(self.events_sell, True, price)

            TradesApi.create_sell_order(self.symbol, 500)

        if self.state != self.state_z:
            self.state_z = self.state

            print(self.state, time.ctime(time.time()), price)


if __name__ == "__main__":

    pass

    # TradesApi.create_sell_order(symbols="TRXETH")
