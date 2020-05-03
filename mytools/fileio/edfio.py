import numpy as np
import pyedflib
import os
import sys


def get_dataindex_from_edf(edffile, targetstr, sensor="Thermistor"):
    """
    read datas from edf file
    str is an array or a list of the channel you wanna use, the function
    will give you all the channels that have those strings.
    If you don't wanna a channel from a specific sensor, just give the arg

    return
        list: channel numbers
    """
    if type(targetstr) == str:
        signal_lables = np.array(edffile.getSignalLabels())
        signal_index = []
        for i, signal_lable in enumerate(signal_lables):
            if signal_lable.find(targetstr) >= 0:
                if edffile.getSignalHeader(i)["transducer"] != sensor:
                    signal_index.append(i)
        return signal_index
    else:
        signal_index = []
        for i in targetstr:
            signal_index += get_dataindex_from_edf(edffile, i)
        return signal_index


def get_signal_from_edf(edffile, index, isclose=True):
    """
    get signal and frequency from edffile
    input:
        EdfReader(or str) : edffile
        int, str(or list) : channal's index
        isclose           : only when edffile is a string, this is useful, if it is true, the edffile will be closed
                            else, the edfreader will be also returned
    return:
        list : signals
        list : frequencys
        list : labels

    """
    if type(edffile) == str:
        edffile = pyedflib.EdfReader(edffile)
        signal, freq, label = get_signal_from_edf(edffile, index)
        if isclose:
            edffile._close()
            return signal, freq, label
        else:
            return signal, freq, label, edffile
    if type(index) == int:
        return edffile.readSignal(index), edffile.getSignalHeader(index)['sample_rate'], edffile.getLabel(index)
    elif type(index) == str:
        newindex = get_dataindex_from_edf(edffile, index)
        return get_signal_from_edf(edffile, newindex)
    else:
        if type(index[0]) == int:
            index_len = len(index)
            signals = np.empty(index_len, dtype=np.object)
            freq = np.empty(index_len)
            label = np.empty(index_len, dtype=np.object)
            for i, ii in enumerate(index):
                signals[i], freq[i], label[i] = get_signal_from_edf(edffile, ii)
            return (signals, freq, label)
        else:
            index = get_dataindex_from_edf(edffile, index)
            return get_signal_from_edf(edffile, index)


def save_signal(signals, freqs, labels, patid, path=None, starttime=None):
    """
    save signals to txt files
    """
    if path is None:
        path = "./" + patid + "/"
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    if type(freqs) != np.ndarray:
        f = open(path + labels + ".dat", "w")
        old_stdout = sys.stdout
        sys.stdout = f
        if starttime is not None:
            print(starttime)
        time = np.arange(0, signals.size / freqs, 1/freqs)
        for i in range(time.size):
            print("%f \t %f" % (time[i], signals[i]))
        sys.stdout = old_stdout
        f.close()
    else:
        for i in range(freqs.size):
            save_signal(signals[i], freqs[i], labels[i], patid, path, starttime)
