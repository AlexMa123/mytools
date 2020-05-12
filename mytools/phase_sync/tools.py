import mkl_fft
import numba
import numpy as np


@numba.njit("c16[:](c16[:])", fastmath=True)
def modifyfft(x):
    N = x.size
    if N % 2 == 0:
        x[1:N // 2] = x[1:N // 2] * 2
        x[N // 2 + 1:] = 0
    else:
        x[1:(N + 1) // 2] = x[1:(N + 1) // 2] * 2
        x[(N + 1) // 2:] = 0
    return x


def hilbert(signal):
    """
    Compute the analytic signal, using the Hilbert transform.
    """
    Xf = mkl_fft.fft(signal)
    Xf = modifyfft(Xf)
    x = mkl_fft.ifft(Xf)
    return x


def phase(signal, zeromean=True):
    signal = signal - np.mean(signal)
    a_s = hilbert(signal)
    return np.arctan2(a_s.imag, a_s.real)
