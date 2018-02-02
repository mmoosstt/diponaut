import numpy
import binance.client
import traceback
import xml.etree.ElementTree as et
import time
import os
import h5py
import time


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


class TradeApi(object):

    def __init__(self, symbol="TRXETH", time_delta=10, file_path_data="./data_sim", file_path_config=""):
        self._simulator = TradeSimulator(symbol=symbol, time_delta=time_delta, file_path=file_path_data)
        self.time_delta = time_delta
        self.symbol = symbol
        self.start_time = time.time()

    def getTradeData(self, startTime, endTime):

        _pos = self._simulator.ring_pos

        data = TradeData()
        data.value_open = self._simulator.ring_value_open[_pos]
        data.value_close = self._simulator.ring_value_close[_pos]
        data.value_mean_quantity = self._simulator.ring_value_mean_quantity[_pos]
        data.value_max = self._simulator.ring_value_max[_pos]
        data.value_min = self._simulator.ring_value_min[_pos]
        data.quantity = self._simulator.ring_quantity[_pos]
        data.trades_count = self._simulator.ring_trades_count[_pos]
        data.trades_time = self.start_time

        self.start_time += self.time_delta

        if _pos > self._simulator.ring_size:
            self._simulator.ring_pos = 0
        else:
            self._simulator.ring_pos += 1

        return data

    def create_buy_order(self, quantity=100):
        pass

    def create_sell_order(self, quantity=100):
        pass


class TradeSimulator(object):

    def __init__(self, symbol='TRXETH', time_delta=10, file_path="./data_sim"):

        self.time_delta = time_delta
        self.time_last_update = 0
        self.symbol = symbol

        _data = TradeData()
        self.ring_size = int(60 * 60 * 24 / time_delta)
        self.ring_data_filepath = "{0}/{1}-{2}s-{3}.hdf".format(
            file_path, symbol, time_delta, "sim")
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


if __name__ == "__main__":
    api = TradeApi(symbol="TRXETH", time_delta=10, file_path_data="../data_sim", file_path_config="")
    _t = api.getTradeData(1, 1)
    print(_t)
