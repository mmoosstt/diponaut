import time
import h5py
import os
import numpy
import threading
from logic.TradeGlobals import GloVar


class TradeInterfaceNotInitialised(Exception):
    pass


class Logger(object):

    def __init__(self, file_path="./data/config.xml"):
        self.trade_interface = None
        self.time_delta = GloVar.get("cyclic_task_main")
        self.time_last_update = 0
        self.ring_size = int(60 * 60 * 24 / self.time_delta)
        self.ring_data_filepath = file_path
        self.ring_pos = int(0)
        self.ring_trades_count = numpy.array([0] * self.ring_size, dtype=numpy.int)
        self.ring_trades_time = numpy.array([time.time()] * self.ring_size, dtype=numpy.double)
        self.ring_value_mean_quantity = numpy.array([0.] * self.ring_size, dtype=numpy.double)
        self.ring_value_max = numpy.array([0.] * self.ring_size, dtype=numpy.double)
        self.ring_value_min = numpy.array([0.] * self.ring_size, dtype=numpy.double)
        self.ring_value_close = numpy.array([0.] * self.ring_size, dtype=numpy.double)
        self.ring_value_open = numpy.array([0.] * self.ring_size, dtype=numpy.double)
        self.ring_quantity = numpy.array([0.] * self.ring_size, dtype=numpy.double)

        if not os.path.isfile(self.ring_data_filepath):
            self.save_storage()

        self.load_storage()

    def init_trade_interface(self, trade_interface):
        self.trade_interface = trade_interface

    def load_storage(self):
        _f = h5py.File(self.ring_data_filepath, 'r')
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

    def save_storage(self, file_path=None):

        if file_path != None:
            self.ring_data_filepath = file_path

        _f = h5py.File(self.ring_data_filepath, 'w')
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

        if self.trade_interface != None:
            _trade = self.trade_interface.getTradeData(_startTime, _endTime)
        else:
            raise TradeInterfaceNotInitialised

        if _trade != None:
            self.time_last_update = _endTime

            self.ring_pos = self.ring_pos + 1
            if self.ring_pos == self.ring_size:
                self.ring_pos = 0

            self.ring_trades_count[self.ring_pos] = _trade.trades_count
            self.ring_trades_time[self.ring_pos] = _trade.trades_time
            self.ring_value_close[self.ring_pos] = _trade.value_close
            self.ring_value_max[self.ring_pos] = _trade.value_max
            self.ring_value_min[self.ring_pos] = _trade.value_min
            self.ring_value_mean_quantity[self.ring_pos] = _trade.value_mean_quantity
            self.ring_value_open[self.ring_pos] = _trade.value_open
            self.ring_quantity[self.ring_pos] = _trade.quantity
