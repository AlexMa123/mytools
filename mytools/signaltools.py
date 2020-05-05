"""
Tools used to analysis signal
"""
import numpy as np
from mkl_fft import fft
from .phase_sync.tools import hilbert, phase
from numba import jit


def powerspectrum(signal, freq=1, removemean=True):
    """
    calculate power spectrum of a given signal
    Input:
        numpy.ndarray: signal
        num          : frequency
        removemean   : whether to remove the mean value or not
    return
        numpy.ndarray: frequency
        numpy.ndarray: powerspectrum
    """
    if removemean:
        signal = signal - np.mean(signal)
    fft_result = fft(signal)
    size = signal.size
    spectrum = np.abs(fft_result[:size//2]) ** 2
    f = np.fft.fftfreq(size, 1/freq)
    return f[:size//2], spectrum


@jit
def interp1dlinear(x, y, xx):
    """
    Linear interpolate 1-D function
    Input:
        x(numpy.array) : old x
        y(numpy.array) : old y
        xx(numpy.array) : new y
    return:
        (numpy.array)  : new y
    """
    result = np.zeros_like(xx)
    i = 0
    istart = 0
    if xx[i] < x[0]:
        while xx[i] <= x[0]:
            result[i] = y[0]
            i += 1
    for j in range(i, result.size):
        while x[istart] < xx[j]:
            istart += 1
            if istart == y.size:
                break
        if istart == y.size:
            result[j:] = y[-1]
            break
        if x[istart] == xx[j]:
            result[j] = y[istart]
            continue
        slope = (y[istart] - istart - 1]) / (x[istart] - x[istart - 1])
        result[j] = y[istart - 1] + slope * (xx[j] - x[istart - 1])
    return result


@numba.njit
def nfreq(signal, n=1):
    """
    n times the signal's frequency
    """
    if n == 1:
        return signal
    else:
        new_signal = np.empty((signal.size - 1)* n + 1)
        new_signal[::n] = signal
        diff = np.diff(signal)
        for i in range(1, n):
            new_signal[i::n] = signal[:-1] + diff * i / n
        return new_signal


def resample(signal, old_freq, new_freq, method="interp"):
    """
    resample the signal from an old frequency to a new frequency
    """
    if old_freq == new_freq:
        return signal
    if old_freq < new_freq:
        if new_freq % old_freq == 0:
            return nfreq(signal, new_freq // old_freq)
        else:
            t_old = np.arange(0, 1/old_freq * signal.size, 1/old_freq)
            t_new = np.arange(0, 1/new_freq * signal.size, 1/new_freq)
            return interp1dlinear(t_old, signal, t_new)
    else:
        if method == "interp":
            n = 0
            #while n * old_freq % new_freq != 0:
            #    n += 1
            #signal = nfreq(signal, n)
            while (n + old_freq) % new_freq != 0:
                n += 1
            if n != 0:
                t1 = np.arange(0, signal.size / old_freq, 1 / old_freq)
                t2 = np.arange(0, signal.size / old_freq, 1 / (old_freq + n))
                signal = interp1dlinear(t1, signal, t2)
            N = (old_freq + n) // new_freq
        elif method == "nfreq":
            n = 1
            while n * old_freq % new_freq != 0:
                n += 1
            signal = nfreq(signal, n)
            N = (old_freq * n) // new_freq
        iend = signal.size - signal.size % (N)
        signal = signal[:iend].reshape(-1, N)
        #return signal
        return np.mean(signal, axis=1)