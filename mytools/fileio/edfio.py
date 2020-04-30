import numpy as np


def get_dataindex_from_edf(edffile, str, sensor="Thermistor"):
    """
    read datas from edf file
    str is an array or a list of the channel you wanna use, the function
    will give you all the channels that have those strings.
    If you don't wanna a channel from a specific sensor, just give the arg

    return
        list: channel numbers
    """
    signal_lables = np.array(edffile.getSignalLabels())
    signal_index = []
    for i, signal_lable in enumerate(signal_lables):
        if signal_lable.find(str) >= 0:
            if edffile.getSignalHeader(i)["transducer"] != sensor:
                signal_index.append(i)
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
        return edffile.readSignal(index), edffile.getSignalHeader(index)['sample_rate']
    else:
        return [edffile.readSignal(i) for i in index], [edffile.getSignalHeader(i)['sample_rate'] for i in index]
