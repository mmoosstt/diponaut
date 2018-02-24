import os
import logic.TradeLogger as tl
import numpy
import matplotlib.pyplot as plt
import scipy
import scipy.signal

# play ground development of fft analysis

np = numpy

if __name__ == "__main__":
    os.chdir(os.path.abspath("../"))
    _path = "./data_storage/XVGETH/XVGETH_2018_02_22_10s-logger.hdf"

    _l = tl.Logger(_path)

    _x = numpy.concatenate((_l.ring_trades_time[_l.ring_pos:], _l.ring_trades_time[:_l.ring_pos]))
    _y = numpy.concatenate((_l.ring_value_mean_quantity[_l.ring_pos:], _l.ring_value_mean_quantity[:_l.ring_pos]))

    x = 1

    _b, _a = scipy.signal.butter(2, 0.05)
    _y, _x = scipy.signal.filtfilt(_b, _a, (_y, _x), axis=1)

    t = _x
    sp = np.fft.fft(_y)
    freq = np.fft.fftfreq(_x.shape[-1], d=10)
    plt.plot(freq, abs(sp))
    plt.show()

    N = _x.shape[-1]
    # sample spacing
    T = 1.0 / 10.
    x = np.linspace(0.0, N * T, N)
    y = _y
    yf = scipy.fftpack.fft(y)
    xf = np.linspace(0.0, 1.0 / (2.0 * T), N / 2)

    #plt.plot(_x, _y)
    plt.savefig("dummy.png")
