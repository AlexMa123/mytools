import numpy as np


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
    fft_result = np.fft.fft(signal)
    size = signal.size
    spectrum = np.abs(fft_result[:size//2]) ** 2
    f = np.fft.fftfreq(size, 1/freq)
    return f[:size//2], spectrum