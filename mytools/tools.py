"""
tools used by the other files
"""

import datetime
from datetime import timedelta


def str_to_float(duration):
    """
    This is for Alice event files, change duration to float type
    """
    x = duration.find("(")
    if x == -1:
        return float(duration)
    else:
        return float(duration[:x])


def get_time_diff(str_day, str_time, starttime):
    temp_time = str_day + ":" + str_time
    d = datetime.datetime.strptime(temp_time, "%d.%m.%Y:%H:%M:%S")
    return (d - starttime).seconds


def get_time_diff_embla(str_day, str_time, starttime):
    if str_day.find(".") != -1:
        temp_time = str_day[:] + ":" + str_time
        d = datetime.datetime.strptime(temp_time, "%d.%m.%Y:%H:%M:%S")
    else:
        temp_time = str_day + ":" + str_time
        d = datetime.datetime.strptime(temp_time, "%d/%m/%Y:%H:%M:%S")
    time_diff = (d - starttime).seconds
    if time_diff >= 0:
        return time_diff
    else:
        return time_diff + 24 * 3600


def get_time_diff_somn(str_day, str_time, starttime):
    if str_day.find(".") != -1:
        temp_time = str_day[:-1] + ":" + str_time
        d = datetime.datetime.strptime(temp_time, "%d.%m.%Y:%H:%M:%S")
    else:
        temp_time = str_day + ":" + str_time
        d = datetime.datetime.strptime(temp_time, "%d/%m/%Y:%H:%M:%S")
    time_diff = (d - starttime).seconds
    if time_diff >= 0:
        return time_diff
    else:
        return time_diff + 24 * 3600


def time_delta(edfstarttime, time_str):
    """
    time_str should be "hour:minite:second"
    """
    if time_str[0] == " ":
        time_str = time_str[1:]
    h, m, s = int(time_str[:2]), int(time_str[3:5]), int(time_str[6:])
    year, month, days = edfstarttime.year, edfstarttime.month, edfstarttime.day
    add_a_day = False
    if h >= 24:
        h -= 24
        add_a_day = True
    new_time = datetime(year, month, days, h, m, s)
    if add_a_day:
        new_time = new_time + timedelta(days=1)
    deltat = (new_time - edfstarttime)
    return deltat.seconds + deltat.days * 24 * 3600
