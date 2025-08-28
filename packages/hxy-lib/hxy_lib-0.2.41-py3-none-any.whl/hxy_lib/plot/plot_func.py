import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes  # 基础类型
import scienceplots
import allantools
from hxy_lib.utils.dev_import_func import KK_data_read_single
from scipy import signal


def thesis_plot(figwidth=1, widht_ratio=0.75, twinx=False, grid=True):
    # Define colormap
    """
    规定论文绘图格式

    :parameter
    -----------
    figwidth: int/float
              图像宽度，默认1，表示A4的单栏宽度

    Returns
    -------
    handle
        fig, ax的句柄

    Examples
    --------
    fig, ax = thesis_plot(figwidth=1)
    """
    upper = mpl.cm.Blues(np.arange(256))
    lower = np.ones((int(256/4),4))
    for i in range(3):
        lower[:,i] = np.linspace(1, upper[0,i], lower.shape[0])
    cmap0 = np.vstack(( lower, upper ))
    cmap0 = mpl.colors.ListedColormap(cmap0, name='myColorMap0', N=cmap0.shape[0])

    plt.style.use(['science'])

    plt.rcParams.update({
        "text.usetex": False,
        "font.family": "serif",
        "font.serif": "times new roman",
        "mathtext.fontset":"stix",
        "font.size":10,
        "savefig.bbox": "standard"})
    plt.rcParams['figure.figsize'] = (6.0, 4.0) # 设置figure_size尺寸
    plt.rcParams['image.interpolation'] = 'nearest' # 设置 interpolation style
    plt.rcParams['image.cmap'] = 'gray' # 设置 颜色 style
    plt.rcParams['savefig.dpi'] = 300 #图片像素
    plt.rcParams['figure.dpi'] = 300 #分辨率

    # 获取默认颜色循环的颜色列表
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']

    # 定义左轴（奇数颜色：1, 3, 5...）和右轴（偶数颜色：0, 2, 4...）
    right_colors = [colors[i] for i in range(len(colors)) if i % 2 != 0]  # 奇数索引
    left_colors = [colors[i] for i in range(len(colors)) if i % 2 == 0]  # 偶数索引

    col_width = 3.375  # inch(半个A4宽度)
    fontsize = np.array([10,9,6.7])*2

    fig = plt.figure(figsize=[col_width * 1.05 * figwidth, col_width * widht_ratio * figwidth], facecolor='w')
    fig_width = col_width * 1.05 * figwidth
    fig_hight = col_width * 0.75 * figwidth
    left_abs = col_width * 1.05 * 0.15
    left_ratio = left_abs / fig_width
    if twinx:
        right_abs = col_width * 1.05 * 0.15
    else:
        right_abs = col_width * 1.05 * 0.1
    width_ratio = 1 - (right_abs + left_abs) / fig_width
    # ax1 = fig.add_axes([0.22, 0.15, 0.75, 0.75])
    # ax1 = fig.add_axes([0.15, 0.15, 0.75, 0.75])
    ax1 = fig.add_axes([left_ratio, 0.15, width_ratio, 0.75])
    bwidth = 0.75
    ax1.spines['top'].set_linewidth(bwidth)
    ax1.spines['bottom'].set_linewidth(bwidth)
    ax1.spines['left'].set_linewidth(bwidth)
    ax1.spines['right'].set_linewidth(bwidth)
    ax1.xaxis.set_tick_params(which='minor', bottom=True, top=True)
    ax1.yaxis.set_tick_params(which='minor', left=True, right=True)

    ax1.tick_params(axis='both', which='major', length=3, width=0.75, labelsize=6)
    ax1.tick_params(axis='both', which='minor', length=1.5, width=0.75, labelsize=6)
    if grid:
        ax1.grid(which='both', linestyle='--', zorder=0, alpha=0.5)
    else:
        ax1.grid(False)
    if twinx:
        ax2 = ax1.twinx()
        ax1.set_prop_cycle(color=left_colors)  # 左轴使用奇数颜色
        ax2.set_prop_cycle(color=right_colors)  # 右轴使用偶数颜色
        ax2.tick_params(axis='both', which='major', length=3, width=0.75, labelsize=6)
        ax2.tick_params(axis='both', which='minor', length=1.5, width=0.75, labelsize=6)

        return fig, ax1, ax2
    else:
        return fig, ax1

def linear_fit_plt(ax_handle, temp_input, voltage_input, gain, text_xy, label_list, unit_str = 'Hz/K'):
    """
        绘制输入x和y数据的去中心散点图，并且进行线性拟合，绘制拟合曲线，打印拟合斜率。(主要用于温漂拟合和数据绘图）

        Args:
            ax_handle (Axes): 绘图轴句柄
            x_array (array): x坐标数据
            y_array (array): y坐标数据
            gain(float): y坐标增益，绘图和计算斜率时除以此增益
            legend_list(list[str]):数据和拟合的图例名称字符串列表
            lable_tuple(truple(str)):x和y坐标的标签字符串元组
            unit_str(str):拟合斜率单位字符串



        Returns:
            None

        Example:

        """

    voltage_mean = np.mean(voltage_input)
    voltage_input = [(x - voltage_mean) / gain for x in voltage_input]
    slope, intercept = np.polyfit(temp_input, voltage_input, 1)
    slope_uV = slope * 1e6
    fitted_temp = np.linspace(np.min(temp_input), np.max(temp_input), 1000)
    fitted_digital = slope * fitted_temp + intercept

    ax_handle.plot(temp_input, voltage_input, marker='o', ls='None', label=label_list[0])
    ax_handle.plot(fitted_temp, fitted_digital, lw=2, label=label_list[1])
    # 获取当前坐标轴范围
    xmin, xmax = ax_handle.get_xlim()
    ymin, ymax = ax_handle.get_ylim()
    if slope_uV > 0:
        # 动态计算文本位置（例如右上角）
        text_x = xmin + 0.8 * (xmax - xmin)  # 向右偏移10%
        text_y = ymax - 0.8 * (ymax - ymin)  # 向下偏移10%
        ha_text = 'right'
    else:
        # 动态计算文本位置（例如右下角）
        # text_x = xmax - 0.1 * (xmax - xmin)  # 向右偏移10%
        text_x = xmin + 0.1 * (xmax - xmin)  # 向右偏移80%
        text_y = ymax - 0.65 * (ymax - ymin)  # 向下偏移10%
        ha_text = 'left'
    # plt.text(text_xy[0], text_xy[1], 'slope: %.3f uV/K' % slope_uV)
    # unit_str = 'Hz/K'
    # plt.text(text_x, text_y, ('slope: %.3f ' + unit_str) % slope,
    # ha='right', va='top',
    # bbox=dict(facecolor='white', alpha=0.8))
    # plt.text(text_x, text_y, ('slope: %.3f ' + unit_str) % slope)
    if unit_str == 'Hz/K':
        ax_handle.text(text_x, text_y, ('slope: %.3f ' + unit_str) % slope, ha=ha_text)
    elif unit_str == 'uV/K':
        ax_handle.text(text_x, text_y, ('slope: %.3f ' + 'μV/K') % slope_uV, ha=ha_text)
    else:
        ax_handle.text(text_x, text_y, ('slope: %.3e ' + unit_str) % slope, ha=ha_text)
    # plt.xlabel('Temperature')
    # plt.ylabel('Input Voltage (V)')
    ax_handle.set_xlabel(r'Temperature ($^\circ$C)')
    ax_handle.set_ylabel('Frequency (Hz)')
    # ax_handle.set_ylabel('Voltage(V)')
    plt.legend()
    plt.grid()


def KK2adev_plt(figwidth,path, name_root, name_order_list, fs, channel, label_list, fc, s_index=(0, -1), detrend=True, plt_en=[True, True]):

    data_list = []
    t_list = []
    for i in name_order_list:
        name = name_root + str(i) + '.txt'
        _, _, data = KK_data_read_single(path, name, channel=channel)
        # plt.plot(data)
        # plt.show()
        data = data[s_index[0]:s_index[1]]
        if detrend:
            data = signal.detrend(data)
        data_list.append(data)
        t = np.linspace(0, len(data) / fs, len(data))
        t_list.append(t)
    if plt_en[0]:
        fig, ax1 = thesis_plot(figwidth=figwidth)
        for i in range(len(name_order_list)):
            ax1.plot(t_list[i], data_list[i], alpha=0.8, label=label_list[i])
        ax1.set_xlabel(r'Time(s)')
        ax1.set_ylabel(r'Frequency(Hz)')
        plt.legend()
        plt.show()

    marker_list = ['o', 'd', 's', '^']
    t_list = []
    ad_list = []

    for i in range(len(data_list)):
        (t, ad, ade, adn) = allantools.oadev(data_list[i], rate=fs, data_type="freq", taus='octave')
        t_list.append(t)
        ad_list.append(ad/fc)
    if plt_en[1]:
        fig, ax1 = thesis_plot(figwidth=figwidth)
        for i in range(len(data_list)):
            ax1.plot(t_list[i], ad_list[i], alpha=0.8, marker=marker_list[i], label=label_list[i])
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        ax1.set_xlabel(r'$\tau$(s)')
        ax1.set_ylabel(r'$\sigma(\tau)$')
        plt.legend()
        plt.show()
    return t_list, ad_list