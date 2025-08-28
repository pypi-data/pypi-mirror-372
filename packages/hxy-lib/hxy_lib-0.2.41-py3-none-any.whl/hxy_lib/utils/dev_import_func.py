from datetime import datetime, date, timedelta
import time
import csv
import subprocess
import sys
from importlib import resources
from pathlib import Path
import numpy as np

def KK_data_read_single(path: str, name: str, begin: int=0, end: int=-1, channel: float='CH2'):
    t = []
    t_data = []
    f_1 = []
    with open(path + name, 'r') as file:
        userlines = file.readlines()
        file.close()
    for line in userlines[begin:end]:
        datetime_obj = datetime.strptime('20' + line.split()[0] + line.split()[1], "%Y%m%d%H%M%S.%f")
        t.append(time.mktime(datetime_obj.timetuple()) + datetime_obj.microsecond / 1E6)
        t_data.append(datetime_obj)
        if channel == 'CH1':
            f_1.append(float(line.split()[3]))
        elif channel == 'CH2':
            f_1.append(float(line.split()[4]))
        elif channel == 'CH3':
            f_1.append(float(line.split()[5]))
        elif channel == 'CH4':
            f_1.append(float(line.split()[6]))

    return t, t_data, f_1

def daq780_import(path, name, column, target_type='float'):
    data_list = []
    with open (path+name, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if target_type == 'float':
                data_list.append(float(row[column]))
            else:
                data_list.append(row[column])
    return data_list


def parse_fft_file(file_path):
    # 初始化元信息字典和数据容器
    metadata = {}
    data_lines = []

    with open(file_path, 'r', encoding='utf-8') as file:

        for line in file:
            line = line.strip()
            # 解析元信息（键值对）
            if ':' in line and not line.startswith(('X[Hz]', '   ')):
                key, value = [s.strip() for s in line.split(':', 1)]
                metadata[key] = value
            # 捕获数据行（科学计数法数字）
            elif line and line[0].isdigit() or line.startswith('-'):
                data_lines.append(line)

    # 将数据转换为 NumPy 数组
    data = np.array([list(map(float, line.split())) for line in data_lines])
    return metadata, data

def SRS780data_read(path, name, start_index=4):
    with resources.path("hxy_lib.bin", "srtrans.exe") as exe_path:
        subprocess.run([str(exe_path), path+'data\\'+name+'.78D', path+'data\\'+name + '.txt'])
    metadata, data = parse_fft_file(path+'data\\'+name+'.txt')
    psd = dbvpk2v2hz(data[:, 1], metadata)
    return data[start_index:, 0], psd[start_index:]

def srs_concatenate(path, name_list, start_index=4):
    f_list= []
    psd_list = []
    for i in range(len(name_list)):
        f, psd = SRS780data_read(path, name_list[i], start_index)
        f_list.append(f)
        psd_list.append(psd)
        f_concate = f_list[0]
        psd_concate = psd_list[0]
        for i in range(len(f_list)-1):
            for j in range(len(f_list[i+1])):
                if f_list[i+1][j] >= f_list[i][-1]:
                    break
            f_concate = np.concatenate((f_concate, f_list[i+1][j:]))
            psd_concate = np.concatenate((psd_concate, psd_list[i+1][j:]))
    return f_concate, psd_concate

def dbvpk2v2hz(dbvpk_data, meta_dbv):
    span = float(meta_dbv['Span'].split()[0])
    unit = meta_dbv['Span'].split()[1]
    if unit == 'kHz':
        span = span * 1e3
    fft_lines = int(meta_dbv['FFT Lines'].strip())
    delta_f = span / fft_lines/2
    fs = span * 2
    if meta_dbv['Averaging Mode'] == 'None':
        Number_of_Avg = 1
    else:
        Number_of_Avg = int(meta_dbv['Number of Avg'].strip())
    if meta_dbv['Window'] == 'BMH':
        # BMH窗的修正系数 (假设为4-term Blackman-Harris)
        CG = 0.42  # 相干增益
        ENBW = 2.0  # 等效噪声带宽 (bins)
    scale = (CG ** 2) / (ENBW * Number_of_Avg)  # 窗函数和平均修正
    # 单位转换
    Vpk = 10 ** (dbvpk_data / 20)  # dBVpk → Vpk
    V2_Hz = (Vpk ** 2) * scale  / delta_f # V²/Hz
    #V2_Hz = 0.25 * Vpk**2/delta_f
    return V2_Hz

