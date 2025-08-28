from datetime import datetime, date, timedelta
import numpy as np
from scipy.io import loadmat
from scipy.signal import welch
#from scipy.integrate import trapz
from scipy.integrate import trapezoid
import math


def time_str_to_seconds(time_str:str)-> int:
    """
        DAQ970的yy:mm:dd:hh:mm:ss字符串数据转为起点为0的秒

        parameter
        -----------
        time_str: str
                  DAQ970的yy:mm:dd:hh:mm:ss时间戳字符串

        Returns
        -------
        int
            以其实时间为0时刻的秒

        Examples
        --------
        second = time_str_to_seconds(time_str)
        """
    dt = datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S")

    # 计算与UNIX纪元(1970-01-01)的时间差
    seconds = (dt - datetime(1970,1,1)).total_seconds()
    return seconds


def average_downsample(arr: list[float], new_length: int) -> np.ndarray:
    """
            将数组降采样平均到目标长度

            parameter
            -----------
            arr: list[float]
                原始数据列表或数组
            new_length: int
                        降采样平均后的数据长度

            Returns
            -------
            array[float]
                降采样平均后的数组

            Examples
            --------
            downsample_array = average_downsample(raw_array, 100)
            """
    if len(arr) < new_length:
        raise ValueError("New length must be smaller than original length for downsampling")

    chunk_size = len(arr) / new_length
    result = []
    for i in range(new_length):
        start = int(i * chunk_size)
        end = int((i + 1) * chunk_size)
        result.append(np.mean(arr[start:end]))
    return np.array(result)

def mat2psd(path, name, na=100):
    """
                从路径读取.mat数据并计算其功率谱密度。

                parameter
                -----------
                path: str
                    目标文件路径字符串
                name: str
                     目标文件名(需要带后缀）
                na: int
                    窗函数平均长度

                Returns
                -------
                array[float]
                    傅里叶频率
                array[float]
                    数据的功率谱密度(V^2/Hz)

                Examples
                --------
                f, PSD = mat2psd(path, name, 100)
                """
    data_file = loadmat(path+name, mat_dtype=True)
    data = data_file['A']
    data = data.flatten(order='C')
    fs_array = data_file['Tinterval']
    fs = 1/fs_array[0]
    print(fs)
    nx = len(data)
    #na = 100
    w = np.hanning(np.floor(nx/na))
    freq, psd = welch(data, fs, w)
    return freq, psd


def psd_to_allan(frequencies, psd, taus, D, fc):
    """
    将PSD转换为艾伦方差
    参数：
        frequencies : 频率数组 (Hz)
        psd        : 对应的PSD值 (Hz²/Hz)
        taus       : 目标平均时间数组 (s)
    返回：
        (taus, allan_var) : 艾伦方差值
    """
    allan_var = np.zeros_like(taus)

    for i, tau in enumerate(taus):
        integrand = 4 * psd * (np.sin(np.pi * frequencies * tau) ** 4) / (np.pi * frequencies * tau) ** 2
        # 处理f=0的奇点
        integrand[frequencies == 0] = 0
        allan_var[i] = trapezoid(integrand, frequencies)
        '''
        sum = 0
        for j in range(1, len(frequencies)):
            sum = sum + psd[j]*(frequencies[j]-frequencies[j-1])*4 * (np.sin(np.pi * frequencies[j] * tau)**4) / (np.pi * frequencies[j] * tau)**2

        allan_var[i] = sum
        '''

    return taus, np.sqrt(allan_var) / D / fc

def K_mn_theory(m, n, dx, dy, gamma_x, gamma_y, w0=365e-6, d=0.1, r2=1):
    """
        计算模式匹配时的耦合效率
        参数：
            m : x方向阶数
            n : y方向阶数
            dx : x方向位移
            dy : y方向位移
            gamma_x : x方向旋转
            gamma_y : y方向旋转
            w0 : 束腰半径
            d : 腔长
            r2 : M2曲率半径（M1为无穷大）
        返回：
            eta_mn : HGmn的耦合效率
    """
    w0 = 365*1e-6
    d = 0.1
    r2 = 1
    z2 = d
    z0 = np.sqrt(d*(r2-d))
    X_ = dx/w0 - (z2/ z0 - 1j) * np.sin(gamma_x) / (w0/z0)
    X = np.conjugate(X_)
    Y_ = (dy)/w0 - (z2/ z0 - 1j) * np.sin(gamma_y) / (w0/z0)
    Y = np.conjugate(Y_)
    Sg_x = 1/math.factorial(m) * (X_)**m
    Sg_y = 1/math.factorial(n) * (Y_)**n
    '''
    for u in range(m//2+1):
        Sg_x = Sg_x + X_**(m - 2 * u)/math.factorial(m - 2 * u)
    for v in range(n//2+1):
        Sg_y = Sg_y + Y_**(n - 2 * v)/math.factorial(n - 2 * v)
    '''
    Ex = np.exp(-X_ * X/2 - 1j * dx/w0 * np.sin(gamma_x) / (w0/z0))
    Ey = np.exp(-Y_ * Y/2 - 1j * (dy)/w0 * np.sin(gamma_y) / (w0/z0))
    return np.abs(Ex*Ey*Sg_x*Sg_y)**2 * math.factorial(m) * math.factorial(n)