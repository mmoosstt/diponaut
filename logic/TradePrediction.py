import time
import h5py
import os
import scipy
import scipy.signal
import numpy
import PySide.QtCore
from logic.TradeGlobals import GloVar


class PredictionData(object):

    def __init__(self):

        self.event_price = 0
        self.event_buy = 0
        self.event_sell = 0
        self.event_zc = False
        self.event_rising = False
        self.event_time = time.time()


class Prediction(PySide.QtCore.QObject):
    signal_prediction_data = PySide.QtCore.Signal(PredictionData)

    def __init__(self, file_path="./data"):
        PySide.QtCore.QObject.__init__(self)

        self.time_delta = GloVar.get("cyclic_task_main")  # s
        self.ring_size = int(60 * 60 * 24 / self.time_delta)
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
        self.prediction = PredictionData()

        self.ring_data_filepath = file_path

        if not os.path.isfile(self.ring_data_filepath):
            self.save_storage()

        self.load_storage()

    def load_storage(self):
        _f = h5py.File(self.ring_data_filepath, 'r')
        self.trades_time = numpy.array(_f['trades_time'], dtype=numpy.double)
        self.trades_median = numpy.array(_f['trades_median'], dtype=numpy.double)
        self.trades_filt1 = numpy.array(_f['trades_filt1'], dtype=numpy.double)
        self.trades_filt2 = numpy.array(_f['trades_filt2'], dtype=numpy.double)
        self.trades_err = numpy.array(_f['trades_err'], dtype=numpy.double)
        self.trades_buy = numpy.array(_f['trades_buy'], dtype=numpy.double)
        self.trades_sell = numpy.array(_f['trades_sell'], dtype=numpy.double)
        _f.close()

    def save_storage(self, file_path=None):

        if file_path != None:
            self.ring_data_filepath = file_path

        _f = h5py.File(self.ring_data_filepath, 'w')
        _f.create_dataset('trades_time', data=self.trades_time)
        _f.create_dataset('trades_median', data=self.trades_median)
        _f.create_dataset('trades_filt1', data=self.trades_filt1)
        _f.create_dataset('trades_filt2', data=self.trades_filt2)
        _f.create_dataset('trades_err', data=self.trades_err)
        _f.create_dataset('trades_buy', data=self.trades_buy)
        _f.create_dataset('trades_sell', data=self.trades_sell)
        _f.close()

    def update(self, logger):

        _trades_time = numpy.concatenate((logger.ring_trades_time[logger.ring_pos:],
                                          logger.ring_trades_time[:logger.ring_pos]))
        numpy.copyto(self.trades_time, _trades_time)

        _trades_raw = numpy.concatenate((logger.ring_value_mean_quantity[logger.ring_pos:],
                                         logger.ring_value_mean_quantity[:logger.ring_pos]))

        numpy.copyto(self.trades_raw, _trades_raw)

        # predic raising or fallin global tendencies
        b, a = scipy.signal.butter(2, GloVar.get("filt1_hz"))
        _trades_filt1 = scipy.signal.filtfilt(b, a, (self.trades_raw, self.trades_time), axis=1)
        numpy.copyto(self.trades_filt1, _trades_filt1[0])

        _trades_filt1_diff = scipy.diff((self.trades_filt1, self.trades_time), axis=1)[0]
        GloVar.set("filt1_grad", numpy.mean(_trades_filt1_diff[-1 * abs(GloVar.get("filt1_grad_range")):]) * self.time_delta)

        # predic raising or fallin global tendencies
        b, a = scipy.signal.butter(2, GloVar.get("filt2_hz"))
        _trades_filt2 = scipy.signal.filtfilt(b, a, (self.trades_raw, self.trades_time), axis=1)
        numpy.copyto(self.trades_filt2, _trades_filt2[0])

        _trades_filt2_diff = scipy.diff((self.trades_filt2, self.trades_time), axis=1)[0]
        numpy.copyto(self.trades_filt2_diff[1:], _trades_filt2_diff)
        GloVar.set("filt2_grad", numpy.mean(_trades_filt2_diff[-1 * abs(GloVar.get("filt2_grad_range")):]) * self.time_delta)

        # calc median deviation
        _trades_err = (self.trades_filt1 - self.trades_filt2)
        numpy.copyto(self.trades_err, _trades_err)

        b, a = scipy.signal.butter(2, 0.001)
        self.trades_err_filt = scipy.diff((self.trades_err, self.trades_time), axis=1)[0]

        # steigung trades error
        _trades_err_diff = scipy.diff(_trades_err)

        # predicted trade level, zc zero crossings
        _trades_err_diff_zc = (_trades_err_diff[:-1] * _trades_err_diff[1:]) < 0.
        _trades_err_diff_zc_value = _trades_err_diff_zc * self.trades_err[1:-1]
        numpy.copyto(self.trades_err_diff_zc[2:], _trades_err_diff_zc_value)

        # calculate buy and sell limits
        _v = numpy.mean(self.trades_filt2[-11:-1])

        # min +- 0.2 %
        _trade_level_buy = _v * ((100 - max(0.2, GloVar.get("factor_buy_offset"))) / 100.) - _v
        _trade_level_sell = _v * ((100 + max(0.2, GloVar.get("factor_sell_offset"))) / 100.) - _v

        numpy.copyto(self.trades_sell[:-1], self.trades_sell[1:])
        self.trades_sell[len(self.trades_sell) - 1] = _trade_level_sell

        numpy.copyto(self.trades_buy[:-1], self.trades_buy[1:])
        self.trades_buy[len(self.trades_buy) - 1] = _trade_level_buy

        pdata = PredictionData()
        pdata.event_price = numpy.mean(self.trades_raw[-6:-1])
        pdata.event_buy = _trades_err[-1:][0] < _trade_level_buy
        pdata.event_sell = _trades_err[-1:][0] > _trade_level_sell
        pdata.event_zc = True in _trades_err_diff_zc[-20:]
        pdata.event_rising = (self.trades_filt2_diff[-1:][0]) >= 0
        pdata.event_time = self.trades_time[-1:][0]

        self.prediction = pdata
