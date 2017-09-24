import numpy as np
from scipy import sparse
import math


class freezing_simu(object):
    """Documentation for simu"""

    def __init__(self, **kwargs):
        self.kf = 0.425
        self.IO = 1000
        self.Hf = 283920.485 * self.IO
        self.Tf = -0.78
        self.Tbase = -40
        self.Cs = 2216.9 * self.IO
        self.C1 = 3597.2 * self.IO
        self.c = (self.Hf - self.Cs * (self.Tf - self.Tbase)) / (
            (self.Tf - self.Tbase
            ) / self.Tbase**2 + 1 / self.Tf - 1 / self.Tbase)
        self.b = (self.Hf - self.c / self.Tf + self.c / self.Tbase) / (
            self.Tf - self.Tbase)
        self.a = -self.b * self.Tbase - self.c / self.Tbase
        self.aa = -6.71e-3
        self.bb = 0.265
        self.cc = -13.7e-4
        self.Ta = kwargs['Ta']
        self.Tp = kwargs['Tp']
        self.Tinit = (np.ones([1, 23]) * self.Tp).transpose()
        self.dt = 30
        self.dx = 0.005
        self.k_iron = 73
        self.h_top = kwargs['ha']
        self.h_bottom = 1/(1/kwargs['ha']+kwargs['dp']/self.k_iron)

    @np.vectorize
    def enthalpy(self, T):
        if T > self.Tf:
            H = self.C1 * (T - self.Tf) + self.Hf
        else:
            H = self.a + self.b * T + self.c / T
        return H

    @np.vectorize
    def temh(self, H):
        # 计算温度值
        if H > self.Hf:
            T = (H - self.Hf) / self.C1 + self.Tf
        else:
            T = (H - self.a - math.sqrt((H - self.a)**2 - 4 * self.b * self.c)) / 2 / self.b
        return T

    # def thermalcon(self, T):
    #     # 计算T温度下的导热系数值,thermal conductivity relative to temperature(C)
    #     if T < self.Tf:
    #         k = self.kf + self.aa * (T - self.Tf) + self.bb * (1 / T - 1 /
    #                                                            self.Tf)
    #     elif T == self.Tf:
    #         k = self.kf
    #     else:
    #         k = self.kf + self.cc * (T - self.Tf)
    #     return k

    @np.vectorize
    def Uvalue(self, T):
        # 计算T温度对应的U值，U值为导热系数和温度值的结合，U是认为设定的一个值，
        # 不是导热系数。
        # 取参考温度Tref为self.Tf，即初始冻结点温度
        if T < self.Tf:
            U = (self.aa * T**2 / 2 + self.bb * math.log(abs(T)) +
                 (self.kf - self.aa * self.Tf - self.bb / self.Tf) * T)
            -(self.aa * self.Tf**2 / 2 + self.bb * math.log(abs(self.Tf)) +
              (self.kf - self.aa * self.Tf - self.bb / self.Tf) * self.Tf)
        elif T == self.Tf:
            U = 0
        else:
            U = (self.cc * T**2 / 2 + (self.kf - self.cc * self.Tf) * T
            ) - (self.cc * self.Tf**2 / 2 +
                 (self.kf - self.cc * self.Tf) * self.Tf)
        return U

    def fd5(self, Told, Hold):
        # Uold = np.zeros(Told.shape)
        # Hnew = np.zeros(Told.shape)
        # Tnew = np.zeros(Told.shape)
        f = np.zeros(Told.shape)
        B = np.array([[1, -2, 0], [1, -2, 2], [1, -2, 1], [1, -2, 1],
                      [1, -2, 1], [1, -2, 1], [1, -2, 1], [1, -2, 1],
                      [1, -2, 1], [1, -2, 1], [1, -2, 1], [1, -2, 1],
                      [1, -2, 1], [1, -2, 1], [1, -2, 1], [1, -2, 1],
                      [1, -2, 1], [1, -2, 1], [1, -2, 1], [1, -2, 1],
                      [1, -2, 1], [2, -2, 1], [0, -2, 1]])
        B1 = B * self.dt / self.dx**2
        Y = sparse.dia_matrix(
            (B1.transpose(), np.array([-1, 0, 1])), shape=(23, 23))
        f[0, 0] = -2 * self.dt * self.h_top * (Told[0, 0] - self.Ta) / self.dx
        f[22, 0] = -2 * self.dt * self.h_bottom * (Told[22, 0] - self.Ta) / self.dx
        Uold = self.Uvalue(self, Told)
        Hnew = Y * Uold + f + Hold
        Tnew = self.temh(self, Hnew)
        return Tnew, Hnew

    def simu(self):
        TT = self.Tinit
        HH = self.enthalpy(self, TT)
        T_all = TT
        H_all = HH
        Tc = self.Tp
        Ts_top = self.Tp
        Ts_bottom = self.Tp
        qq_top = 0
        qq_bottom = 0
        for n in range(5000):
            [Tnew, Hnew] = self.fd5(TT, HH)
            TT = Tnew
            HH = Hnew
            T_all = np.column_stack((T_all, Tnew))
            H_all = np.column_stack((H_all, Hnew))

            Tc = np.row_stack((Tc, Tnew.max()))
            Ts_top = np.row_stack((Ts_top, Tnew[0]))
            Ts_bottom = np.row_stack((Ts_bottom, Tnew[22]))
            qq_top = np.row_stack((qq_top, self.h_top * (Tnew[0] - self.Ta)))
            qq_bottom = np.row_stack((qq_bottom, self.h_bottom * (Tnew[22] - self.Ta)))
            print(n)
            if Tnew[11] < -15:
                break

        # T_temp = np.zeros(T_all.shape)
        # H_temp = np.zeros(H_all.shape)
        # for i in range(T_all.shape[0]):
        #     T_temp[-i, :] = T_all[i, :]
        #     H_temp[-i, :] = H_all[i, :]

        # T_all = np.row_stack((T_temp[1:, :], T_all))
        # H_all = np.row_stack((H_temp[1:, :], H_all))
        T_all = T_all.transpose()
        H_all = H_all.transpose()
        time = np.array(range(n+2)) * 30 / 3600
        return Tc, Ts_top, Ts_bottom, qq_top, qq_bottom, time, T_all, H_all



# Tc, Ts_top, Ts_bottom, qq_top, qq_bottom, time, T_all, H_all = freezing_simu(Ta=-30, Tp=30, ha=10, dp=10).simu()
