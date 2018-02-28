import os
import logic.TradeLogger as tl
import numpy
import matplotlib.pyplot as plt
import scipy
import scipy.signal
import logic.TradeGroundControl as TradeGroundControl
from logic.TradeGlobals import GloVar
import time
from numpy import dtype

# play ground development of fft analysis

np = numpy

if __name__ == "__main__":
    os.chdir(os.path.abspath("../"))

    symbols = ["XVGETH", "BNBETH", "TRXETH"]

    for symbol in symbols:

        GloVar.set("trade_symbol", symbol)

        _path = "./data_storage/{0}".format(symbol)

        _res = TradeGroundControl.FileName.find_file_ids(_path, 'logger')

        _keys = sorted(_res.keys())

        _X = numpy.array([], dtype=np.float)
        _Y = numpy.array([], dtype=np.float)

        _min = -1e10
        _max = 1e10

        print(symbol)

        for _key in _keys:

            _match_dict = _res[_key]
            _file_name = TradeGroundControl.FileName.create_file_id(_match_dict)

            _file_path = "{0}/{1}".format(_path, _file_name)

            _l = tl.Logger(_file_path)

            _x = numpy.concatenate((_l.ring_trades_time[_l.ring_pos:], _l.ring_trades_time[:_l.ring_pos]))
            _y = numpy.concatenate((_l.ring_value_mean_quantity[_l.ring_pos:], _l.ring_value_mean_quantity[:_l.ring_pos]))

            # _x and _y value plausibilisation

            _min = max(min(_x), _min)
            _max = max(_x)

            _true_arr = numpy.where(((_x < _max) & (_x > _min) & (_y > 1e-21) & (_y != np.nan) & (_x != np.nan)))
            _x = _x[_true_arr]
            _y = _y[_true_arr]

            _X = numpy.concatenate((_X, _x))
            _Y = numpy.concatenate((_Y, _y))

            _min = _max + 10

        plt.plot(_X, _Y)  # , freq, abs(sp))
        plt.savefig("./data_storage/{0}_history.png".format(symbol))
        plt.clf()

        if 0:  # no filtering
            _b, _a = scipy.signal.butter(2, 0.5)  # T=20s shanon
            _y, _x = scipy.signal.filtfilt(_b, _a, (_Y, _X), axis=1)

            plt.plot(_x, _y)
            plt.savefig("./data_storage/{0}_history_filtered.png".format(symbol))
            plt.clf()

        N = _x.shape[-1]
        T = 10  # s
        # sample spacing

        _yf = np.absolute(np.fft.fft(_y))[1:int(N / 2)]
        _xfreq = np.fft.fftfreq(N)[1:int(N / 2)]

        if 0:
            _p = plt.semilogy(_xfreq, _yf)
            plt.xlim((0, 0.01))
            plt.savefig("./data_storage/{0}_fft.png".format(symbol))
            plt.clf()

        plt.hist(_yf, 100, (0, 0.01))
        plt.savefig("./data_storage/{0}_fft_hist.png".format(symbol))
        plt.clf()
