"""
My functions used to calculate breathing frequency
"""
import numpy as np
import biosppy.signals.tools as st
from scipy.signal import hilbert
from biosppy.signals.resp import resp


def freq_from_biosppy(signal, freq):
    """
    get frequency through biosppy's fucntion, it's based on zero-cross method
    Input
        signal(np.array) : breathing signal
        freq(num)        : signal's frequency
    return
        t(np.array)      : time (where the zero cross happen)
        f(np.array)      : breathing frequency
    """
    result = resp(signal, freq, False)
    t = result['resp_rate_ts']
    f = result['resp_rate']
    return t, f


def freq_from_phase(signal, freq):
    """
    breathing frequency through phase method
    Input
        signal(np.array) : breathing signal
        freq(num)        : signal's frequency
    return
        t(np.array)      : time (where one breathing cycle starts)
        f(np.array)      : breathing frequency

    """
    signal, _, _ = st.filter_signal(signal=signal,
                                    ftype='butter',
                                    band='bandpass',
                                    order=2,
                                    frequency=[0.1, 0.35],
                                    sampling_rate=freq)
    # pass a filter to remove the noise.
    if freq >= 4:
        new_freq = 4
        windows_size = freq / new_freq
        while(windows_size - int(windows_size) != 0):
            new_freq = new_freq + 1
            windows_size = freq / new_freq
        windows_size = int(windows_size)
        signal = np.mean(signal.reshape(-1, windows_size), axis=1)
        # resample the signal to 4 Hz
        signal = signal - np.mean(signal)

    sorted_signal = np.sort(signal)
    threshold = sorted_signal[-int(sorted_signal.size * 0.2)] * 0.005
    # choose a threshold

    phase = np.arctan2(signal, hilbert(signal))
    phase[np.abs(signal) < threshold] = 0
    # Set the phase where the signal is under the threshold to zero
    phase_diff = np.diff(phase)
    fire_position = np.where(phase_diff < - 0.5 * np.pi)[0]
    # find where the breathing cycle start
    fire_position = fire_position[phase[fire_position + 1] != 0]

    fire_position = fire_position / new_freq
    # change index to seconds
    f = 1 / np.diff(fire_position)
    t = fire_position[1:]

    return t, f