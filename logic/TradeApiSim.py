import os
import numpy
import h5py
import time
import traceback
from logic.TradeGlobals import GloVar
from logic import TradeGlobals


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


class Api(object):

    def __init__(self, file_path):
        self._simulator = TradeSimulator(file_path)
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

        self.start_time += GloVar.get("cyclic_task_main")

        if int(self._simulator.ring_size - 1) == int(_pos):
            self._simulator.ring_pos = 0
        else:
            self._simulator.ring_pos += 1

        return data

    def create_buy_order(self):
        pass

    def create_sell_order(self):
        pass


class TradeSimulator(object):

    def __init__(self, file_path):

        _data = TradeData()
        self.ring_size = int(60 * 60 * 24 / GloVar.get("cyclic_task_main"))
        self.ring_data_filepath = file_path
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
    api = ApiSim("../data_sim/TRXETH-10s-sim.hdf")
    print(api.getTradeData(1, 1))
    api.create_buy_order()
    api.create_sell_order()