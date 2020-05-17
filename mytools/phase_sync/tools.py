import mkl_fft
import numba
from .. import signaltools as st
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


def phase_m(phase, m=1, thread=2.7):

    fire_position_index = np.where(phase >= thread)
    # if fire_position_index[0][-1] == phase.size - 1:
    #     fire_position_index[0] = fire_position_index[0][:-2]
    if fire_position_index[0][-1] == phase.size - 1:
        fire_position_temp = np.where(phase[fire_position_index[0][:-1] + 1] < - thread)[0]
    else:
        fire_position_temp = np.where(phase[fire_position_index[0] + 1] < - thread)[0]
    fire_position_temp = fire_position_index[0][fire_position_temp] + 1
    if m == 1:
        return phase, fire_position_temp
    fire_position = np.zeros(fire_position_temp.size + 2, dtype=np.int64)
    fire_position[0] = 0
    fire_position[-1] = phase.size
    fire_position[1:-1] = fire_position_temp

    new_phase = np.empty(phase.size, dtype=np.float64)
    delta = np.array([np.pi * (2 * i + 1) for i in range(m)])
    n = 0
    for i in range(fire_position.size - 1):
        new_phase[fire_position[i]: fire_position[i + 1]] = phase[fire_position[i]: fire_position[i + 1]] + delta[n]
        n = n + 1
        n = n % m
    new_phase = new_phase - (delta[-1] + np.pi) / 2
    return new_phase, fire_position_temp[m-1::m]


def synchogram(phase, r_index, freq_phase, freq_r=None, m=1, thread=2):
    if freq_r is None:
        if type(freq_phase) == np.ndarray:
            t_phase = freq_phase
        else:
            t_phase = np.arange(0, phase.size/freq_phase, 1/freq_phase)
        phase, fire_position = phase_m(phase, m, thread)
        t_phase[fire_position - 1] = t_phase[fire_position]
        phi_mt = st.interp1dlinear(t_phase, phase, r_index)
        return phi_mt
    else:
        phase, fire_position = phase_m(phase, m, thread)
        phase_index = r_index * float(freq_phase) / float(freq_r)
        int_index = np.floor(phase_index).astype(np.int64)
        frac_index = phase_index - int_index
        phi_mt = np.empty(r_index.size)
        phi_mt = phase[int_index]
        if int_index[-1] == phase.size - 1:
            int_index = int_index[:1]
            add_term = (phase[int_index+1] - phase[int_index])
            index = np.where(add_term <= - thread * m)
            add_term[index] = 0
            add_term = frac_index * add_term
        else:
            add_term = (phase[int_index+1] - phase[int_index])
            index = np.where(add_term <= - thread * m)
            add_term[index] = 0
            add_term = frac_index * add_term
        phi_mt = phi_mt + add_term
        return phi_mt


def phase(signal, zeromean=True):
    if zeromean:
        signal = signal - np.mean(signal)
    a_s = hilbert(signal)
    return np.arctan2(a_s.imag, a_s.real)
