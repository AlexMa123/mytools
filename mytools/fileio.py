"""
Used to read the files I needed. Like rri, event files.
"""
import pandas as pd
import codecs
import pyedflib
import numpy as np
import datetime
# from . import tools
from .tools import get_time_diff, get_time_diff_embla, get_time_diff_somn, str_to_float


def read_rri(rri_file, edf_starttime=None):
    """
    get R peaks and the start time of the file
    """
    f = open(rri_file, 'r')
    f.readline()
    f.readline()
    """
    get start time of this rri file
    """
    rr_startdate = f.readline()
    num_start = rr_startdate.find("=") + 1
    rr_startdate = rr_startdate[num_start:-1]
    rr_starttime = f.readline()
    num_start = rr_starttime.find("=") + 1
    rr_starttime = rr_starttime[num_start:-1]
    file_starttime = rr_startdate + " " + rr_starttime
    try:
        file_starttime = datetime.datetime.strptime(file_starttime,
                                                    "%d.%m.%Y %H:%M:%S")
    except ValueError:
        file_starttime = datetime.datetime.strptime(file_starttime,
                                                    "%Y-%m-%d %H:%M:%S")
    """
    get frequency of rri
    """
    line = f.readline()
    num_start = line.find("=") + 1
    freq = int(line[num_start:])
    f.close()
    """
    read R position
    """
    data = np.loadtxt(rri_file, skiprows=7)
    if edf_starttime is not None:
        data = data + (file_starttime - edf_starttime).seconds * freq
    return data, freq



def get_data_from_edf(edffile, str, sensor="Thermistor"):
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


def alice_csv(csvfile, starttime, apnea_type):
    """
    args:
        csvfile: file name
        starttime: when the edf file started
        apnea_type: list(str): the kind of apnea you wanna search
    return:
        array of array: apneas start time from a starttime. (in seconds)
        array of array: apnea end time.
    """
    if type(apnea_type) == list:
        apnea_type = np.array(apnea_type)
    csv_file = pd.read_csv(csvfile,
                           encoding="windows-1252",
                           sep=";",
                           usecols=[0, 2, 4, 5, 13])
    ApneaStarttime = np.empty(apnea_type.size, dtype=object)
    ApneaEndtime = np.empty(apnea_type.size, dtype=object)
    for i in range(apnea_type.size):
        index_apnea = np.where(csv_file['Ereignistyp'] == apnea_type[i])
        valid = csv_file.loc[index_apnea]['Validierung'].values
        apnea_time = csv_file.loc[index_apnea]['Zeit'].values
        days = csv_file.loc[index_apnea]['Datum'].values
        duration = csv_file.loc[index_apnea]['Dauer'].values
        real_apnea_index = np.where(valid != '-')
        if real_apnea_index[0].size == 0:
            ApneaStarttime[i] = np.array([])
            ApneaEndtime[i] = np.array([])
            continue
        vec_fun = np.vectorize(get_time_diff, excluded=['starttime'])
        time_diff = vec_fun(days[real_apnea_index], apnea_time[real_apnea_index],
                            starttime)
        vec_fun = np.vectorize(str_to_float)
        duration = vec_fun(duration[real_apnea_index])
        ApneaStarttime[i] = time_diff
        ApneaEndtime[i] = ApneaStarttime[i] + duration
    return ApneaStarttime, ApneaEndtime


def embla_csv(csvfile, starttime, apnea_type):
    if type(apnea_type) == list:
        apnea_type = np.array(apnea_type)
 
    f = codecs.open(csvfile, 'r', "windows-1252")
    for i in range(3):
        f.readline()
    startday = f.readline()
    startday = startday[startday.find(":\t") + 2:startday.find(":\t") + 12]
    print(startday)
    f.close()
    csv_file = pd.read_csv(csvfile,
                           encoding="windows-1252",
                           sep="\t",
                           skiprows=38,
                           usecols=[2, 3, 4],
                           names=["time", "type", "duration"])
    ApneaStarttime = np.empty(apnea_type.size, dtype=object)
    ApneaEndtime = np.empty(apnea_type.size, dtype=object)
    for i in range(apnea_type.size):
        index_apnea = np.where(csv_file['type'] == apnea_type[i])
        ApneaStarttime[i] = csv_file.loc[index_apnea]['time'].values
        Duration = csv_file.loc[index_apnea]['duration'].values
        if ApneaStarttime[i].size == 0:
            continue
        else:
            vec_fun = np.vectorize(get_time_diff_embla,
                                   excluded=['str_day', 'starttime'])
            ApneaStarttime[i] = vec_fun(startday, ApneaStarttime[i], starttime)
            ApneaEndtime[i] = ApneaStarttime[i] + Duration
    return ApneaStarttime, ApneaEndtime


def somnoscreen_csv(csvfolder, starttime, apnea_type):
    if type(apnea_type) == list:
        apnea_type = np.array(apnea_type)
 
    f = open(csvfolder + "Flow Events.txt", "r")
    f.readline()
    startday = f.readline()
    startday = startday[startday.find(":") + 2:-10]
    f.close()
    csv_file = pd.read_csv(csvfolder + "Flow Events.txt",
                           encoding="windows-1252",
                           sep=";",
                           skiprows=5,
                           usecols=[0, 1, 2],
                           names=["time", "duration", "type"])
    ApneaStarttime = np.empty(apnea_type.size, dtype=object)
    ApneaEndtime = np.empty(apnea_type.size, dtype=object)

    for i in range(apnea_type.size):
        index_apnea = np.where(csv_file['type'] == apnea_type[i])
        ApneaStarttime[i] = csv_file.loc[index_apnea]['time'].values
        if ApneaStarttime[i].size != 0:
            for j in range(ApneaStarttime[i].size):
                ApneaStarttime[i][j] = ApneaStarttime[i][j][:8]
        Duration = csv_file.loc[index_apnea]["duration"].values
        if ApneaStarttime[i].size == 0:
            continue
        else:
            vec_fun = np.vectorize(get_time_diff_somn,
                                   excluded=['str_day', 'starttime'])
            ApneaStarttime[i] = vec_fun(startday, ApneaStarttime[i], starttime)
            ApneaEndtime[i] = ApneaStarttime[i] + Duration

    return ApneaStarttime, ApneaEndtime

