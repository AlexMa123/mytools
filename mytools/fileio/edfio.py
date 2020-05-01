import numpy as np


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


def get_signal_from_edf(edffile, index):
    """
    get signal and frequency from edffile
    input:
        EdfReader    : edffile
        int(or list) : channal's index
    return:
        list : signals
        list : frequencys

    """
    if type(index) == int:
        return edffile.readSignal(index), edffile.getSignalHeader(index)['sample_rate'], edffile.getLabel(index)
    elif type(index) == str:
        newindex = get_dataindex_from_edf(edffile, index)
        get_signal_from_edf(edffile, newindex)
    else:
        if type(index[0]) == np.int:
            index_len = len(index)
            signals = np.empty(index_len, dtype=np.object)
            freq = np.empty(index_len)
            label = np.empty(index_len, dtype=np.string_)
            for i, ii in enumerate(index):
                signals[i], freq[i], label[i] = get_signal_from_edf(edffile, ii)
            return signals, freq, label
        else:
            get_signal_from_edf(edffile, get_dataindex_from_edf(edffile, index))
