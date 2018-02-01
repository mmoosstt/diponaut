import time
import h5py
import os
import sys
import traceback
import scipy
import scipy.signal
import numpy
import matplotlib.pyplot as plt
import binance.client
import PySide.QtCore
import threading
import utils.Interfaces


GloVar = utils.Interfaces.IVariables()
GloVar.factor_buy_fix = utils.Interfaces.IVariable(value=1.5, type=float)
GloVar.factor_buy_var = utils.Interfaces.IVariable(value=1., type=float)
GloVar.factor_buy = utils.Interfaces.IVariable(value=0., type=float)
GloVar.factor_sell_fix = utils.Interfaces.IVariable(value=1.5, type=float)
GloVar.factor_sell_var = utils.Interfaces.IVariable(value=1., type=float)
GloVar.factor_sell = utils.Interfaces.IVariable(value=0., type=float)
GloVar.filt1_hz = utils.Interfaces.IVariable(value=0.01, type=float)
GloVar.filt2_hz = utils.Interfaces.IVariable(value=0.001, type=float)
GloVar.filt2_grad_range = utils.Interfaces.IVariable(value=300, type=int)
GloVar.filt2_grad = utils.Interfaces.IVariable(value=0., type=float)
GloVar.state = utils.Interfaces.IVariable(value="undef", type=str)
GloVar.state_buy_time = utils.Interfaces.IVariable(value=0., type=int)
GloVar.state_buy_price = utils.Interfaces.IVariable(value=0., type=float)
GloVar.state_sell_time = utils.Interfaces.IVariable(value=0, type=int)
GloVar.state_sell_price = utils.Interfaces.IVariable(value=0., type=float)
GloVar.order_quantity = utils.Interfaces.IVariable(value=250, type=int)


class BinanceClient(object):

    api = None

    def __init__(self, file_path="./data/BinanceApi.hdf5"):

        if __class__.api == None:
            _f = h5py.File(file_path, 'r')
            self.key = _f['key_storage'].attrs['key']
            self.key_secret = _f['key_storage'].attrs['key_secret']
            _f.close()

            __class__.api = binance.client.Client(self.key,  self.key_secret)


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

    client = None

    def __init__(self, file_path="./data", file_name="BinanceApi.hdf5"):
        if __class__.client == None:
            __class__.client = BinanceClient("{0}/{1}".format(file_path, file_name))

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

            _price = numpy.array(_price, numpy.double)
            _quantity = numpy.array(_quantity, numpy.double)

            data = TradeData()
            data.value_open = _price[0]
            data.value_close = _price[-1:]
            data.value_mean_quantity = numpy.sum(
                _price * _quantity) / numpy.sum(_quantity)
            data.value_max = numpy.max(_price)
            data.value_min = numpy.min(_price)
            data.quantity = numpy.sum(_quantity)
            data.trades_count = len(_price)
            data.trades_time = (min(_time) + max(_time)) / 2.

            return data
        else:
            print('No trades')
            return None

    @staticmethod
    def create_buy_order(symbols='TRXETH', quantity=100):

        _ret = __class__.client.api.create_order(
            symbol=symbols,
            side=binance.client.Client.SIDE_BUY,
            type=binance.client.Client.ORDER_TYPE_MARKET,
            quantity=GloVar.get("order_quantity"))

        print(_ret)

    @staticmethod
    def create_sell_order(symbols="TRXETH", quantity=100):

        _ret = __class__.client.api.create_order(
            symbol=symbols,
            side=binance.client.Client.SIDE_SELL,
            type=binance.client.Client.ORDER_TYPE_MARKET,
            quantity=GloVar.get("order_quantity"))

        print(_ret)


class TradesLogger(object):

    def __init__(self, symbol='TRXETH', time_delta=10, file_path="./data"):
        Start = TradesApi(file_path=file_path)

        self.Prediction = TradesPrediction(symbol, time_delta, file_path)

        self.time_delta = time_delta
        self.time_last_update = 0
        self.symbol = symbol

        _data = TradeData()
        self.ring_size = int(60 * 60 * 24 / time_delta)
        self.ring_data_filepath = "{0}/{1}-{2}s-{3}.hdf".format(
            file_path, symbol, time_delta, "logger")
        self.ring_pos = int(0)
        self.ring_trades_count = numpy.array([_data.trades_count] * self.ring_size, dtype=numpy.int)
        self.ring_trades_time = numpy.array([_data.trades_time] * self.ring_size, dtype=numpy.double)
        self.ring_value_mean_quantity = numpy.array([_data.value_mean_quantity] * self.ring_size, dtype=numpy.double)
        self.ring_value_max = numpy.array([_data.value_max] * self.ring_size, dtype=numpy.double)
        self.ring_value_min = numpy.array([_data.value_min] * self.ring_size, dtype=numpy.double)
        self.ring_value_close = numpy.array([_data.value_open] * self.ring_size, dtype=numpy.double)
        self.ring_value_open = numpy.array([_data.value_close] * self.ring_size, dtype=numpy.double)
        self.ring_quantity = numpy.array([_data.quantity] * self.ring_size, dtype=numpy.double)

        if not os.path.isfile(self.ring_data_filepath):
            self.save_storage(self.ring_data_filepath)

        self.load_storage(self.ring_data_filepath)

    def load_storage(self, file_path):
        _f = h5py.File(file_path, 'r')
        self.ring_trades_count = numpy.array(_f['ring_trades_count'], dtype=numpy.int)
        self.ring_trades_time = numpy.array(_f['ring_trades_time'], dtype=numpy.double)
        self.ring_value_mean_quantity = numpy.array(_f['ring_value_mean_quantity'], dtype=numpy.double)
        self.ring_value_max = numpy.array(_f['ring_value_max'], dtype=numpy.double)
        self.ring_value_min = numpy.array(_f['ring_value_min'], dtype=numpy.double)
        self.ring_value_close = numpy.array(_f['ring_value_close'], dtype=numpy.double)
        self.ring_value_open = numpy.array(_f['ring_value_open'], dtype=numpy.double)
        self.ring_quantity = numpy.array(_f['ring_quantity'], dtype=numpy.double)
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

    def update(self):

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

        self.Prediction.update(self)
        self.save_storage(self.ring_data_filepath)


class TradesPrediction(PySide.QtCore.QObject):

    def __init__(self,  symbol="TRXETH", time_delta=10, storages_path="./data"):
        PySide.QtCore.QObject.__init__(self)

        self.States = TradingStates(symbol, time_delta, storages_path)
        self.time_delta = time_delta  # s
        self.ring_size = int(60 * 60 * 24 / time_delta)
        self.trades_time = numpy.array([0] * self.ring_size, dtype=numpy.double)
        self.trades_err_ana = numpy.array([0] * self.ring_size, dtype=numpy.double)
        self.trades_raw = numpy.array([0] * self.ring_size, dtype=numpy.double)
        self.trades_median = numpy.array([0] * self.ring_size, dtype=numpy.double)
        self.trades_filt1 = numpy.array([0] * self.ring_size, dtype=numpy.double)
        self.trades_filt2 = numpy.array([0] * self.ring_size, dtype=numpy.double)
        self.trades_err_diff_zc = numpy.array([0] * self.ring_size, dtype=numpy.double)
        self.trades_filt2_diff = numpy.array([0] * self.ring_size, dtype=numpy.double)
        self.trades_err = numpy.array([0] * self.ring_size, dtype=numpy.double)
        self.trades_buy = numpy.array([numpy.NaN] * self.ring_size, dtype=numpy.double)
        self.trades_sell = numpy.array([numpy.NaN] * self.ring_size, dtype=numpy.double)

        self.ring_data_filepath = "{0}/{1}-{2}s-{3}.hdf".format(
            storages_path, symbol, time_delta, "prediction")

        if not os.path.isfile(self.ring_data_filepath):
            self.save_storage(self.ring_data_filepath)

        self.load_storage(self.ring_data_filepath)

    def load_storage(self, file_path):
        _f = h5py.File(file_path, 'r')
        self.trades_time = numpy.array(_f['trades_time'], dtype=numpy.double)
        self.trades_median = numpy.array(_f['trades_median'], dtype=numpy.double)
        self.trades_filt1 = numpy.array(_f['trades_filt1'], dtype=numpy.double)
        self.trades_filt2 = numpy.array(_f['trades_filt2'], dtype=numpy.double)
        self.trades_err = numpy.array(_f['trades_err'], dtype=numpy.double)
        self.trades_buy = numpy.array(_f['trades_buy'], dtype=numpy.double)
        self.trades_sell = numpy.array(_f['trades_sell'], dtype=numpy.double)
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

        _dummy = numpy.concatenate((source.ring_trades_time[source.ring_pos:],
                                    source.ring_trades_time[:source.ring_pos]))

        numpy.copyto(self.trades_time, _dummy)

        _dummy = numpy.concatenate((source.ring_value_mean_quantity[source.ring_pos:],
                                    source.ring_value_mean_quantity[:source.ring_pos]))

        numpy.copyto(self.trades_raw, _dummy)

        # predic raising or fallin global tendencies
        b, a = scipy.signal.butter(2, GloVar.get("filt1_hz"))
        _trades_filt1 = scipy.signal.filtfilt(b, a, (self.trades_raw, self.trades_time), axis=1)
        numpy.copyto(self.trades_filt1, _trades_filt1[0])

        # predic raising or fallin global tendencies
        b, a = scipy.signal.butter(2, GloVar.get("filt2_hz"))
        _trades_filt2 = scipy.signal.filtfilt(b, a, (self.trades_raw, self.trades_time), axis=1)
        numpy.copyto(self.trades_filt2, _trades_filt2[0])

        _trades_filt2_diff = scipy.diff((self.trades_filt2, self.trades_time), axis=1)[0]
        numpy.copyto(self.trades_filt2_diff[1:], _trades_filt2_diff)

        # calc median deviation
        _trades_err = (self.trades_filt1 - self.trades_filt2)
        numpy.copyto(self.trades_err, _trades_err)

        # steigung trades error
        _trades_err_diff = scipy.diff(_trades_err)

        # predicted trade level, zc zero crossings
        _trades_err_diff_zc = (_trades_err_diff[:-1] * _trades_err_diff[1:]) < 0.
        _trades_err_diff_zc_value = _trades_err_diff_zc * self.trades_err[1:-1]
        numpy.copyto(self.trades_err_diff_zc[2:], _trades_err_diff_zc_value)

        # weighted limits factor
        _trades_filt2_diff_rel = self.trades_filt2_diff / (numpy.max(self.trades_filt2_diff) - numpy.min(self.trades_filt2_diff))
        _trades_filt2_diff_rel_actual = numpy.mean(_trades_filt2_diff_rel[-1 * int(GloVar.get("filt2_grad_range")):])

        GloVar.set("filt2_grad", _trades_filt2_diff_rel_actual)

        _trade_level_factor_buy_fix = GloVar.get("factor_buy_fix")
        _trade_level_factor_buy_var = GloVar.get("factor_buy_var") * abs(_trades_filt2_diff_rel_actual)

        _trade_level_factor_sell_fix = GloVar.get("factor_sell_fix")
        _trade_level_factor_sell_var = GloVar.get("factor_sell_var") * abs(_trades_filt2_diff_rel_actual)

        if _trades_filt2_diff_rel_actual >= 0:
            _trade_level_sell_factor = _trade_level_factor_sell_fix + _trade_level_factor_sell_var
            _trade_level_buy_factor = _trade_level_factor_buy_fix - _trade_level_factor_buy_var
        else:
            _trade_level_sell_factor = _trade_level_factor_sell_fix - _trade_level_factor_sell_var
            _trade_level_buy_factor = _trade_level_factor_buy_fix + _trade_level_factor_buy_var

        GloVar.set("factor_sell", _trade_level_sell_factor)
        GloVar.set("factor_buy", _trade_level_buy_factor)

        # calc buy and sell limits
        _trade_level_sell = self.trades_err_diff_zc[scipy.where(self.trades_err_diff_zc > 0)]
        _trade_level_sell = numpy.mean(_trade_level_sell) * _trade_level_sell_factor

        numpy.copyto(self.trades_sell[:-1], self.trades_sell[1:])
        self.trades_sell[len(self.trades_sell) - 1] = _trade_level_sell

        _trade_level_buy = self.trades_err_diff_zc[scipy.where(self.trades_err_diff_zc < 0)]
        _trade_level_buy = numpy.mean(_trade_level_buy) * _trade_level_buy_factor

        numpy.copyto(self.trades_buy[:-1], self.trades_buy[1:])
        self.trades_buy[len(self.trades_buy) - 1] = _trade_level_buy

        def update_array(ring, event, price):

            if event:
                ring[len(self.trades_buy) - 1] = price
            else:
                ring[len(self.trades_buy) - 1] = numpy.NaN

        self.save_storage(self.ring_data_filepath)

        _event_price = numpy.mean(self.trades_raw[-6:-1])
        _event_buy = _trades_err[-1:][0] < _trade_level_buy
        _event_sell = _trades_err[-1:][0] > _trade_level_sell
        _event_zc = True in _trades_err_diff_zc[-20:]
        _event_rising = (self.trades_filt2_diff[-1:][0]) >= 0
        _event_time = self.trades_time[-1:][0]

        self.States.update(_event_price, _event_time, _event_buy, _event_sell, _event_zc, _event_rising)


class TradingStates(object):

    def __init__(self, symbol="TRXETH", time_delta=10, storages_path="./data"):
        self.symbol = symbol
        self.state = "start"
        self.state_z = "start"
        self.zc_cnt = 0
        self.ring_size = int(60 * 60 * 24 / time_delta)
        self.events_buy = numpy.array([numpy.NaN] * self.ring_size, dtype=numpy.double)
        self.events_sell = numpy.array([numpy.NaN] * self.ring_size, dtype=numpy.double)
        self.events_zc = numpy.array([numpy.NaN] * self.ring_size, dtype=numpy.double)
        self.events_buy_time = numpy.array([numpy.NaN] * self.ring_size, dtype=numpy.double)
        self.events_sell_time = numpy.array([numpy.NaN] * self.ring_size, dtype=numpy.double)
        self.events_zc_time = numpy.array([numpy.NaN] * self.ring_size, dtype=numpy.double)

        self.ring_data_filepath = "{0}/{1}-{2}s-{3}.hdf".format(
            storages_path, symbol, time_delta, "events")

        if not os.path.isfile(self.ring_data_filepath):
            self.save_storage(self.ring_data_filepath)

        self.load_storage(self.ring_data_filepath)

    def load_storage(self, file_path):
        _f = h5py.File(file_path, 'r')
        self.events_buy = numpy.array(_f['events_buy'], dtype=numpy.double)
        self.events_buy_time = numpy.array(_f['events_buy_time'], dtype=numpy.double)
        self.events_sell = numpy.array(_f['events_sell'], dtype=numpy.double)

        self.events_sell_time = numpy.array(_f['events_sell_time'], dtype=numpy.double)
        self.events_zc = numpy.array(_f['events_zc'], dtype=numpy.double)
        self.events_zc_time = numpy.array(_f['events_zc_time'], dtype=numpy.double)
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

    def update(self, price, time_event, buy_event=False, sell_event=False, zc_event=False, rising_event=False):

        def _add_event(events_arr, event, value):

            if event:
                numpy.copyto(events_arr[:-1], events_arr[1:])
                events_arr[len(events_arr) - 1] = value

        if self.state == "week_buy":
            self.week_buy_cnt += 1
        else:
            self.week_buy_cnt = 0

        if self.state == "week_sell" and sell_event == False:
            self.week_sell_cnt += 1
        else:
            self.week_sell_cnt = 0

        if zc_event:
            self.zc_cnt = min(3, self.zc_cnt + 1)

        else:
            self.zc_cnt = max(0, self.zc_cnt - 1)

        zc_event = False
        if self.zc_cnt >= 3:
            zc_event = True

            _add_event(self.events_zc_time, True, time_event)
            _add_event(self.events_zc, True, price)
            self.save_storage(self.ring_data_filepath)
            GloVar.set("state_buy_price", price)
            GloVar.set("state_buy_time", time_event)

            print("zero crossing")

        if (
            (self.state == "start" or
             self.state == "stro_sell") and
                buy_event == True):

            self.state = "week_buy"
            self.price_week = price

        elif (self.state == "week_buy" and
              (zc_event == True and buy_event == True)):
            self.state = "stro_buy"

            TradesApi.create_buy_order(self.symbol, 500)

            _add_event(self.events_buy_time, True, time_event)
            _add_event(self.events_buy, True, price)
            self.save_storage(self.ring_data_filepath)

        elif (self.state == "stro_buy" and
              sell_event == True):
            self.state = "week_sell"
            self.price_week = price

        elif (self.state == "week_sell" and
              (zc_event == True or
               (sell_event == False and self.week_sell_cnt >= 6)
               )
              ):
            self.state = "stro_sell"

            TradesApi.create_sell_order(self.symbol, 500)

            _add_event(self.events_sell_time, True, time_event)
            _add_event(self.events_sell, True, price)
            self.save_storage(self.ring_data_filepath)
            GloVar.set("state_sell_price", price)
            GloVar.set("state_sell_time", time_event)

        if self.state != self.state_z:
            self.state_z = self.state

            print(self.state, time.ctime(time.time()), price)

            GloVar.set("state", self.state)


if __name__ == "__main__":

    TradesApi.create_sell_order("TRXETH", 500)
    pass
