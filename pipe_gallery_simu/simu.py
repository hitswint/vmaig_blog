import numpy as np
from scipy.optimize import root, fsolve
import random
import string
import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

zh_font = fm.FontProperties(
    fname='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', size=30)


# * parameters for gas
class Gas(object):
    """Documentation for Gas

    """

    def __init__(self, wall_obj, T_in, vel):
        super(Gas, self).__init__()
        self.T_in = T_in
        self.vel = vel
        self.T = np.zeros(1)
        self.rho = 0.7374
        self.Lambda = 0.024 * 1.25
        self.Cm = 2089
        self.D = wall_obj.D_i

    @property
    def Niu(self):
        return 0.00000052546 * (273.15 + self.T[-1])**0.59006 / (
            1 + 105.67 / (273.15 + self.T[-1]))

    @property
    def Re(self):
        return self.vel * self.D / self.Niu

    @property
    def Pr(self):
        return self.Niu / (self.Lambda / (self.rho * self.Cm))

    @property
    def Nu(self):
        return 0.023 * self.Re**0.8 * self.Pr**0.3

    @property
    def alpha(self):
        return self.Nu * self.Lambda / self.D


# * parameters for air
class Air(object):
    """Documentation for Air

    """

    def __init__(self, wall_obj, T_in, vel):
        super(Air, self).__init__()
        self.T_in = T_in
        self.vel = vel
        self.T = np.zeros(1)
        self.rho = 1.29
        self.Lambda = 0.024
        self.Cm = 1007
        self.D = 4 * wall_obj.A_gallery / wall_obj.S_gallery  # 当量直径
        self.Niu = 13.7e-6
        self.Re = self.vel * self.D / self.Niu
        self.Pr = self.Niu / (self.Lambda / (self.rho * self.Cm))
        self.Nu = 0.023 * self.Re**0.8 * self.Pr**0.4
        self.alpha = self.Nu * self.Lambda / self.D


# * parameters for tube wall and gallery
class Wall(object):
    """Documentation for Wall

    """

    def __init__(self, Num_pipegallery, Length_pipegallery, Num, T_gallery):
        super(Wall, self).__init__()
        self.R_insulation = 0.0081 / 52.3 + 0.0029 / 0.42
        # 管道参数
        # 内径610mm
        self.D_i = 0.61
        self.S_i = np.pi * self.D_i
        self.A_i = np.pi * (self.D_i / 2)**2
        # 钢管8.1mm厚，外包聚乙烯冷缠带2.9mm厚。
        self.sigma = 5.67
        self.epsilon_o = 0.79
        self.D_o = 0.632
        self.S_o = np.pi * self.D_o
        self.A_o = np.pi * (self.D_o / 2)**2
        self.T_i = np.zeros(0)
        self.T_o = np.zeros(0)
        # 管廊参数
        self.epsilon_gallery = 0.93
        self.width = 2.7
        self.height = 2.3
        self.D_gallery = 5.4
        # 管廊空气流通截面积。
        self.A_gallery = np.pi * (self.D_gallery / 2)**2 / 4 - self.A_o
        # 管廊空气流场湿周，包括管廊内壁和管道外壁。
        self.S_gallery = self.height + self.width + np.pi * self.D_gallery / 4 + self.S_o

        # 管廊长度与分段数
        self.T_gallery = T_gallery
        self.Num_pipegallery = Num_pipegallery  # 机械通风管廊数量
        self.Length_pipegallery = Length_pipegallery  # 管廊长度
        self.Num = Num  # 管廊有限体积离散分段数
        self.Length = self.Length_pipegallery / self.Num  # 管廊有限体积离散分段长度


# * coefficient for eqs
class Coefficient(object):
    """Documentation for Coefficient

    """

    def __init__(self, gas_obj, air_obj, wall_obj):
        super(Coefficient, self).__init__()
        self.gas = gas_obj
        self.air = air_obj
        self.wall = wall_obj
        # coefficient for eq 1.
        self.c1_gas_0 = -self.gas.Cm * self.gas.rho * self.wall.A_i * self.gas.vel

        # coefficient for eq 2.
        self.c2_air_0 = -self.air.Cm * self.air.rho * self.wall.A_gallery * self.air.vel

        # coefficient for eq 3.
        self.c3_o = -(
            self.wall.D_i + self.wall.D_o) / 2 / self.wall.R_insulation

        # coefficient for eq 4.
        self.c4_i = -(
            self.wall.D_i + self.wall.D_o) / 2 / self.wall.R_insulation
        self.c4_radiation = self.wall.S_o * self.wall.sigma / (
            1 / self.wall.epsilon_o + self.wall.S_o *
            (1 / self.wall.epsilon_gallery - 1) /
            (self.wall.S_gallery - self.wall.S_o))

    @property
    def c1_i(self):
        return -self.gas.alpha * self.wall.S_i * self.wall.Length

    @property
    def c1_gas(self):
        return -self.c1_gas_0 - self.c1_i

    @property
    def c2_o(self):
        return -self.air.alpha * self.wall.S_o * self.wall.Length

    @property
    def c2_gallery(self):
        return -self.air.alpha * (
            self.wall.S_gallery - self.wall.S_o) * self.wall.Length

    @property
    def c2_air(self):
        return -self.c2_air_0 - self.c2_o - self.c2_gallery

    @property
    def c3_gas(self):
        return -self.gas.alpha * self.wall.D_i

    @property
    def c3_i(self):
        return -self.c3_gas - self.c3_o

    @property
    def c4_air(self):
        return -self.air.alpha * self.wall.D_o

    @property
    def c4_o(self):
        return -self.c4_air - self.c4_i


# 燃气温度为x[0:Num]，燃气从0流向Num。
# 空气温度为x[Num:2*Num]，空气从2*Num流向Num。
# 管壁内侧温度为x[2*Num:3*Num]
# 管壁外侧温度为x[3*Num:4*Num]


def f1(x, *args):

    wall_obj = args[0]
    gas_obj = args[1]
    air_obj = args[2]
    c_obj = args[3]
    radiation_included_p = args[4]

    T_gas_in = gas_obj.T_in
    T_air_in = air_obj.T_in
    T_gallery = wall_obj.T_gallery
    Num = wall_obj.Num
    # 保存所有方程的数组。
    y = np.zeros(4 * Num)

    # 第一个节点
    y[0:4] = np.array([
        c_obj.c1_gas * x[0] + c_obj.c1_gas_0 * T_gas_in +
        c_obj.c1_i * x[2 * Num],
        c_obj.c2_air * x[Num] + c_obj.c2_air_0 * x[Num + 1] +
        c_obj.c2_o * x[3 * Num] + c_obj.c2_gallery * T_gallery,
        c_obj.c3_i * x[2 * Num] + c_obj.c3_o * x[3 * Num] +
        c_obj.c3_gas * x[0], c_obj.c4_i * x[2 * Num] + c_obj.c4_o * x[3 * Num]
        + c_obj.c4_air * x[Num]
        # + c_obj.c4_radiation * (((x[3 * Num] + 273.15) / 100)**4 - ((T_gallery + 273.15) / 100)**4)
    ])
    if radiation_included_p:
        y[3] += c_obj.c4_radiation * (((x[3 * Num] + 273.15) / 100)**4 -
                                      ((T_gallery + 273.15) / 100)**4)

    # 最后一个节点
    y[-4:] = np.array([
        c_obj.c1_gas * x[Num - 1] + c_obj.c1_gas_0 * x[Num - 2] +
        c_obj.c1_i * x[3 * Num - 1],
        c_obj.c2_air * x[2 * Num - 1] + c_obj.c2_air_0 * T_air_in +
        c_obj.c2_o * x[4 * Num - 1] + c_obj.c2_gallery * T_gallery,
        c_obj.c3_i * x[3 * Num - 1] + c_obj.c3_o * x[4 * Num - 1] +
        c_obj.c3_gas * x[Num - 1], c_obj.c4_i * x[3 * Num - 1] +
        c_obj.c4_o * x[4 * Num - 1] + c_obj.c4_air * x[2 * Num - 1]
        # + c_obj.c4_radiation * (((x[4 * Num - 1] + 273.15) / 100)**4 - ((T_gallery + 273.15) / 100)**4)
    ])
    if radiation_included_p:
        y[-1] += c_obj.c4_radiation * (((x[4 * Num - 1] + 273.15) / 100)**4 -
                                       ((T_gallery + 273.15) / 100)**4)

    # 迭代每段管廊，每段4个方程。
    for i in range(1, Num - 1):
        y[4 * i:4 * i + 4] = np.array([
            c_obj.c1_gas * x[i] + c_obj.c1_gas_0 * x[i - 1] +
            c_obj.c1_i * x[2 * Num + i],
            c_obj.c2_air * x[Num + i] + c_obj.c2_air_0 * x[Num + i + 1] +
            c_obj.c2_o * x[3 * Num + i] + c_obj.c2_gallery * T_gallery,
            c_obj.c3_i * x[2 * Num + i] + c_obj.c3_o * x[3 * Num + i] +
            c_obj.c3_gas * x[i], c_obj.c4_i * x[2 * Num + i] +
            c_obj.c4_o * x[3 * Num + i] + c_obj.c4_air * x[Num + i]
            # + c_obj.c4_radiation * (((x[3 * Num + i] + 273.15) / 100)**4 - ((T_gallery + 273.15) / 100)**4)
        ])
        if radiation_included_p:
            y[4 * i + 3] += c_obj.c4_radiation * (
                ((x[3 * Num + i] + 273.15) / 100)**4 -
                ((T_gallery + 273.15) / 100)**4)
    return y


# * main
def main(*, Num_pipegallery, Length_pipegallery, Num, T_gallery, T_gas_in,
         T_air_in, V_gas, V_air, radiation_included_p):

    wall_obj = Wall(Num_pipegallery, Length_pipegallery, Num, T_gallery)
    gas_obj = Gas(wall_obj, T_gas_in, V_gas)
    air_obj = Air(wall_obj, T_air_in, V_air)
    c_obj = Coefficient(gas_obj, air_obj, wall_obj)

    for i in range(wall_obj.Num_pipegallery):
        # sol_root = root(f1, np.zeros(4 * wall_obj.Num), (T_gas_in, T_air_in))
        sol_fsolve = fsolve(f1,
                            np.zeros(4 * wall_obj.Num),
                            (wall_obj, gas_obj, air_obj, c_obj,
                             radiation_included_p))
        gas_obj.T_in = sol_fsolve[wall_obj.Num - 1]
        gas_obj.T = np.concatenate((gas_obj.T, sol_fsolve[0:wall_obj.Num]), 0)
        air_obj.T = np.concatenate(
            (air_obj.T, sol_fsolve[wall_obj.Num:2 * wall_obj.Num]), 0)
        wall_obj.T_i = np.concatenate(
            (wall_obj.T_i, sol_fsolve[2 * wall_obj.Num:3 * wall_obj.Num]), 0)
        wall_obj.T_o = np.concatenate(
            (wall_obj.T_o, sol_fsolve[3 * wall_obj.Num:4 * wall_obj.Num]), 0)
        print(i)

    plot_file = 'simu_{}.png'.format(
        ''.join(random.sample(string.ascii_letters + string.digits, 8)))
    fig1 = plt.figure(figsize=(19, 16), dpi=98)
    ax1 = fig1.add_subplot(211)
    ax2 = fig1.add_subplot(212)

    ax1.set_ylim(-11, 11)  # sets y limits
    ax1.tick_params(axis='both', labelsize=18)
    ax1_x = np.arange(0,
                      wall_obj.Length_pipegallery * wall_obj.Num_pipegallery,
                      wall_obj.Length)
    ax1.plot(ax1_x[::5], gas_obj.T[1::5], 'b-o', label='燃气温度', linewidth=1)
    ax1.plot(ax1_x[::5], air_obj.T[1::5], 'm-s', label='空气温度', linewidth=0.2)
    [
        ax1.axvline(x)
        for x in np.linspace(0, wall_obj.Length_pipegallery * wall_obj.
                             Num_pipegallery, wall_obj.Num_pipegallery + 1)
    ]
    ax1.set_xlabel(u'长度(m)', fontproperties=zh_font)
    ax1.set_ylabel(u'温度($\,^\circ\mathrm{C}$)', fontproperties=zh_font)
    ax1.legend(loc='upper right', prop=zh_font)

    ax2_x = np.arange(0,
                      wall_obj.Length_pipegallery * wall_obj.Num_pipegallery,
                      wall_obj.Length)
    ax2.tick_params(axis='both', labelsize=18)
    ax2.plot(ax2_x[::5], wall_obj.T_i[1::5], 'g', label='管壁内表面', linewidth=1.2)
    ax2.plot(ax2_x[::5], wall_obj.T_o[1::5], 'r', label='管壁外表面', linewidth=1.2)
    [
        ax2.axvline(x)
        for x in np.linspace(0, wall_obj.Length_pipegallery * wall_obj.
                             Num_pipegallery, wall_obj.Num_pipegallery + 1)
    ]
    ax2.set_xlabel(u'长度(m)', fontproperties=zh_font)
    ax2.set_ylabel(u'温度($\,^\circ\mathrm{C}$)', fontproperties=zh_font)
    ax2.legend(loc='upper right', prop=zh_font)

    fig1.tight_layout()
    fig1.savefig("media/pipe_gallery_simu/" + plot_file)
    plt.close(fig1)
    return plot_file, '{:.2f} ℃ T_gas_out'.format(
        gas_obj.T[-1]), '{:.2f} ℃ T_air_out'.format(
            air_obj.T[-1]), '{:.2f} ℃ T_wall_i'.format(wall_obj.T_i[
                -1]), '{:.2f} ℃ T_wall_o'.format(wall_obj.T_o[-1])


if __name__ == '__main__':
    result_list = main(
        Num_pipegallery=20,
        Length_pipegallery=500,
        Num=100,
        T_gallery=5,
        T_gas_in=10,
        T_air_in=-10,
        V_gas=5,
        V_air=0.5,
        radiation_included_p=False)
