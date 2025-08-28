import brainpy as bp
import numpy as np
import brainpy.math as bm
from pathlib import Path
import pickle
from bpusdk.BrainpyLib.BrainpyBase import BrainpyBase
import matplotlib.pyplot as plt
import numpy as np
from brainpy._src.dyn.neurons.base import GradNeuDyn
# this version with phi
# addition of phi makes restricted response when T=42 (gate open) 
# this is because self.T_base far away from T_threshold
# negative modulation when T>42.

class HHtemp(GradNeuDyn):
    def __init__(self, size,
                 # 电生理参数
                 E_Na=50.0, gNa17=18.0, gNa18=7.0,
                 E_K=-77.0, gK=4.78, gKA=8.33,
                 E_l=-54.387, gL=0.03,
                 C=1.0, A=1.0,  # C: 膜电容, A: 膜面积
                 refractory=2.0, V_th=0.0,
                 T=6.3, T_threshold=10.0,  # 新增温度参数，T_threshold 为温度门控阈值
                 method='exp_auto',
                 **kwargs):
        super(HHtemp, self).__init__(size=size)
        # 存储参数
        self.E_Na   = E_Na
        self.E_K    = E_K
        self.E_l    = E_l
        self.gNa17  = gNa17  # INa1.7 最大电导
        self.gNa18  = gNa18  # INa1.8 最大电导
        self.gK     = gK     # IK 最大电导
        self.gKA    = gKA    # IKA 最大电导
        self.gL     = gL     # 漏电流电导
        self.C      = C
        self.A      = A
        self.V_th   = V_th
        self.refractory = refractory
        self.T      = T  # 当前温度
        self.T_threshold = T_threshold  # 温度门控阈值
        
        self.Q10 = 20  # 20~40之间
        self.T_threshold = T_threshold  # 温度门控阈值
        # 带温度门控的phi
        T_activate = 42
        T_saturate = 50
        
        phi_raw = self.Q10 ** ((T - self.T_threshold) / 10.0)
        act = 1 / (1 + np.exp(-(T - T_activate) * 3))
        saturate = 1 / (1 + np.exp((T - T_saturate) * 4))
        self.phi = phi_raw * act * saturate
        
        # 定义温度门控函数：当 T >= T_threshold 时开关为 1，否则为 0
        temp_gate = bm.where(self.T >= self.T_threshold, 1.0, 0.0)
        temp_gate = 0.001 + (1 - 0.001) / (1 + bm.exp(-(self.T - self.T_threshold) * 5))
        self.temp_gate = temp_gate

        # 初始条件（统一取 V0 = -70.68 mV）
        V0 = -70.68
        self.V    = bm.Variable(bm.ones(self.num) * V0)
        # INa1.7 的门控变量： m, h, s
        self.m17  = bm.Variable(bm.ones(self.num) * self.m17_inf(V0))
        self.h17  = bm.Variable(bm.ones(self.num) * self.h17_inf(V0))
        self.s17  = bm.Variable(bm.ones(self.num) * self.s17_inf(V0))
        # INa1.8 的门控变量： m, h
        self.m18  = bm.Variable(bm.ones(self.num) * self.m18_inf(V0))
        self.h18  = bm.Variable(bm.ones(self.num) * self.h18_inf(V0))
        # IK 的门控变量： n
        self.nK   = bm.Variable(bm.ones(self.num) * self.nK_inf(V0))
        # IKA 的门控变量： n, h
        self.nKA  = bm.Variable(bm.ones(self.num) * self.nKA_inf(V0))
        self.hKA  = bm.Variable(bm.ones(self.num) * self.hKA_inf(V0))
        
        # 不应期相关
        self.t_last_spike = bm.Variable(bm.ones(self.num) * (-1e7))
        self.spike        = bm.Variable(bm.zeros(self.num, dtype=bool))
        self.refractory   = bm.Variable(bm.zeros(self.num, dtype=bool))
        
        # 定义联合微分方程积分器
        self.integral = bp.odeint(f=self.derivative, method=method,show_code=False)

    
# -----------------------
    # INa1.7 动力学函数
    # -----------------------
    def m17_inf(self, V):
        alpha = 15.5 / (1 + bm.exp((V - 5) / -12.08))
        beta  = 35.2 / (1 + bm.exp((V + 72.7) / 16.7))
        return alpha / (alpha + beta)

    def dm17(self, m17, t, V):
        alpha = 15.5 / (1 + bm.exp((V - 5) / -12.08))
        beta  = 35.2 / (1 + bm.exp((V + 72.7) / 16.7))
        return self.phi * (alpha * (1 - m17) - beta * m17)

    def h17_inf(self, V):
        alpha = 0.38685 / (1 + bm.exp((V + 122.35) / 15.29))
        beta  = -0.00283 + 2.00283 / (1 + bm.exp((V + 5.5266) / -12.70195))
        return alpha / (alpha + beta)

    def dh17(self, h17, t, V):
        alpha = 0.38685 / (1 + bm.exp((V + 122.35) / 15.29))
        beta  = -0.00283 + 2.00283 / (1 + bm.exp((V + 5.5266) / -12.70195))
        return self.phi * (alpha * (1 - h17) - beta * h17)

    def s17_inf(self, V):
        alpha = 0.00003 + 0.00092 / (1 + bm.exp((V + 93.9) / 16.6))
        beta  = 132.05 - 132.05 / (1 + bm.exp((V - 384.9) / 28.5))
        return alpha / (alpha + beta)

    def ds17(self, s17, t, V):
        alpha = 0.00003 + 0.00092 / (1 + bm.exp((V + 93.9) / 16.6))
        beta  = 132.05 - 132.05 / (1 + bm.exp((V - 384.9) / 28.5))
        return self.phi * (alpha * (1 - s17) - beta * s17)

    # -----------------------
    # INa1.8 动力学函数
    # -----------------------
    def m18_inf(self, V):
        alpha = 2.85 - 2.839 / (1 + bm.exp((V - 1.159) / 13.95))
        beta  = 7.6205 / (1 + bm.exp((V + 46.463) / 8.8289))
        return alpha / (alpha + beta)

    def dm18(self, m18, t, V):
        alpha = 2.85 - 2.839 / (1 + bm.exp((V - 1.159) / 13.95))
        beta  = 7.6205 / (1 + bm.exp((V + 46.463) / 8.8289))
        return alpha * (1 - m18) - beta * m18

    def h18_inf(self, V):
        return 1 / (1 + bm.exp((V + 32.2) / 4))

    def dh18(self, h18, t, V):
        h_inf_val = 1 / (1 + bm.exp((V + 32.2) / 4))
        tau = 1.218 + 42.043 * bm.exp(-((V + 38.1) ** 2) / (2 * 15.19 ** 2))
        return (h_inf_val - h18) / tau

    # -----------------------
    # IK 动力学函数
    # -----------------------
    def nK_inf(self, V):
        alpha_n = 0.001265 * (V + 14.273) / (1 - bm.exp(-(V + 14.273) / 10))
        beta_n  = 0.125 * bm.exp(-(V + 55) / 2.5)
        return alpha_n / (alpha_n + beta_n)

    def dnK(self, nK, t, V):
        alpha_n = 0.001265 * (V + 14.273) / (1 - bm.exp(-(V + 14.273) / 10))
        beta_n  = 0.125 * bm.exp(-(V + 55) / 2.5)
        return self.phi * (alpha_n * (1 - nK) - beta_n * nK)

    # -----------------------
    # IKA 动力学函数
    # -----------------------
    def nKA_inf(self, V):
        return (1 / (1 + bm.exp(-(V + 5.4) / 16.4))) ** 4

    def dnKA(self, nKA, t, V):
        n_inf = (1 / (1 + bm.exp(-(V + 5.4) / 16.4))) ** 4
        tau = 0.25 + 10.04 * bm.exp(-((V + 24.67) ** 2) / (2 * 34.8 ** 2))
        return (n_inf - nKA) / tau

    def hKA_inf(self, V):
        return 1 / (1 + bm.exp((V + 49.9) / 4.6))

    def dhKA(self, hKA, t, V):
        h_inf = 1 / (1 + bm.exp((V + 49.9) / 4.6))
        tau = 20 + 50 * bm.exp(-((V + 40) ** 2) / (2 * 40 ** 2))
        return (h_inf - hKA) / tau
    
    # 膜电位微分方程，增加温度门控
    def dV(self, V, t, m17, h17, s17, m18, h18, nK, nKA, hKA, Iext):        
        I_Na17 = self.gNa17 * (m17 ** 3) * h17 * s17 * (V - self.E_Na)
        I_Na18 = self.gNa18 * m18 * h18 * (V - self.E_Na)
        I_K    = self.gK    * nK * (V - self.E_K)
        I_KA   = self.gKA   * nKA * hKA * (V - self.E_K)
        I_L    = self.gL    * (V - self.E_l)
        I_ion  = I_Na17 + I_Na18 + I_K + I_KA + I_L
        # 当温度低于 T_threshold 时，temp_gate=0，离子电流被“关闭”
        return (Iext / self.A - self.temp_gate* I_ion) / self.C

    @property
    def derivative(self):
        return bp.JointEq(
            self.dm17,    # INa1.7 m 门控变量
            self.dh17,    # INa1.7 h 门控变量
            self.ds17,    # INa1.7 s 门控变量
            self.dm18,    # INa1.8 m 门控变量
            self.dh18,    # INa1.8 h 门控变量
            self.dnK,     # IK 的 n 门控变量
            self.dnKA,    # IKA 的 n 门控变量
            self.dhKA,     # IKA 的 h 门控变量
            self.dV,   # 膜电位微分方程
        )
    
    def update(self,x):
        x = 0. if x is None else x
        x = self.sum_current_inputs(self.V.value, init=x)
        
        t  = bp.share.load('t')
        dt = bp.share.load('dt')
        # 联合积分更新所有变量
        m17_new, h17_new, s17_new, m18_new, h18_new, nK_new, nKA_new, hKA_new, V_new = \
            self.integral(self.m17, self.h17, self.s17,
                        self.m18, self.h18, self.nK, self.nKA, self.hKA,self.V,
                        t, x, dt=dt)
        
        # 判断动作电位产生
        spike = bm.logical_and(self.V < self.V_th, V_new >= self.V_th)
        not_refractory = (t - self.t_last_spike) >= self.refractory
        spike = bm.logical_and(spike, not_refractory)
        self.spike.value = spike
        self.t_last_spike.value = bm.where(spike, t, self.t_last_spike)
        
        refractory_mask = (t - self.t_last_spike) < self.refractory

        # 更新状态：处于不应期的神经元保持原状态
        self.V.value    = bm.where(refractory_mask, self.V, V_new)
        self.m17.value  = bm.where(refractory_mask, self.m17, m17_new)
        self.h17.value  = bm.where(refractory_mask, self.h17, h17_new)
        self.s17.value  = bm.where(refractory_mask, self.s17, s17_new)
        self.m18.value  = bm.where(refractory_mask, self.m18, m18_new)
        self.h18.value  = bm.where(refractory_mask, self.h18, h18_new)
        self.nK.value   = bm.where(refractory_mask, self.nK, nK_new)
        self.nKA.value  = bm.where(refractory_mask, self.nKA, nKA_new)
        self.hKA.value  = bm.where(refractory_mask, self.hKA, hKA_new)
 
class EINet(bp.DynamicalSystem):
    def __init__(self, ne, ni, conn, method, allow_multi_conn=True,temp=42):
        super().__init__()        
        self.initState = bm.random.DEFAULT.value
        self.neuron_scale = [ne, ni]
        self.E = HHtemp(size=ne,
                        T=temp,       # 当前温度
                        T_threshold= 42, # 温度门控阈值
                        refractory = 0.0,
                        method=method)
        self.I = HHtemp(size=ni,
                        T=temp,       # 当前温度
                        T_threshold= 42, # 温度门控阈值
                        refractory = 0.0,
                        method=method)
        self.ne = ne
        self.ni = ni

    def update(self, inpE):
        self.E(inpE)
        self.I(inpE)
        # monitor
        return self.E.spike, self.I.spike

    def dump(self,download_path,inpS,inpE,nStep,jit=True,save=True, txt=False): 
        V_init = np.concatenate((self.E.V.value, self.I.V.value), axis=0)
        V_init = np.expand_dims(V_init, axis=0)
        S_init = np.zeros((1, self.ne+self.ni))
        
        vv_init = self.E.V.value[0]
        nK_init = self.E.nK.value[0]
        nKA_init = self.E.nKA.value[0]
        hKA_init = self.E.hKA.value[0]
        m17_init = self.E.m17.value[0]
        h17_init = self.E.h17.value[0]
        s17_init = self.E.s17.value[0]
        m18_init = self.E.m18.value[0]
        h18_init = self.E.h18.value[0]
        
        if isinstance(inpE, list):
            inpE_list = []
            for i in range(len(inpE)):
                repeated = np.ones(nStep[i]) * inpE[i]
                inpE_list.append(repeated)

            inpE = np.concatenate(inpE_list, axis=None)
            inpE = bm.array(inpE)
        else:
            inpE = bm.ones(nStep) * inpE 
            
        runner = bp.DSRunner(
            self, monitors=['E.spike', 'I.spike', 'E.V', 'I.V',
                            'E.nK','E.nKA','E.hKA','E.m17','E.h17','E.s17','E.m18','E.h18'], jit=jit)
        _ = runner.run(inputs=[inpE])
    
        E_sps = runner.mon['E.spike']
        I_sps = runner.mon['I.spike']
        E_V = runner.mon['E.V']
        I_V = runner.mon['I.V']
        
        vv = runner.mon['E.V'][:,0]
        nK = runner.mon['E.nK'][:,0]
        nKA = runner.mon['E.nKA'][:,0]
        hKA = runner.mon['E.hKA'][:,0]
        m17 = runner.mon['E.m17'][:,0]
        h17 = runner.mon['E.h17'][:,0]
        s17 = runner.mon['E.s17'][:,0]
        m18 = runner.mon['E.m18'][:,0]
        h18 = runner.mon['E.h18'][:,0]

        S = np.concatenate((E_sps, I_sps), axis=1)
        S = np.concatenate((S_init, S), axis=0)
        V = np.concatenate((E_V, I_V), axis=1)
        V = np.concatenate((V_init, V), axis=0)

        if save == True:
            download_path = f"{download_path}/soft_data"
            download_dir = Path(download_path)
            download_dir.mkdir(exist_ok=True,parents=True)
            np.save(download_dir / "N_V.npy", V)
            np.save(download_dir / "N_spike.npy", S)

            test = BrainpyBase(self, inpE,{})
            conn_matrix = test.get_connection_matrix()
            cv = test.cv
            with open(f'{download_dir}/connection.pickle', 'wb') as handle:
                pickle.dump(conn_matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

        else:
            fig, ax = plt.subplots(2, 1, figsize=(10, 2.5))
            ax[0].plot(
                runner.mon.ts,                # time
                V[1:, 0]  
            )

            ax[0].set_ylim(-80, 60)
            ax[0].set_xlabel('Time (ms)')
            ax[0].set_ylabel('V (mV)')
            ax[0].legend(fontsize=8)

            ax[1].plot(
                runner.mon.ts,                # time
                S[1:, 0]  
            )
            plt.show()
            plt.savefig("./fig")
            
            S = np.sum(S,axis=1)
            print(S)
        
        if txt == True:
            download_path = f"{download_path}/soft_data_txt"
            download_dir = Path(download_path)
            download_dir.mkdir(exist_ok=True,parents=True)        
            for iStep in range(nStep+1):
                np.savetxt(f"{download_path}/V_step_{iStep:03}.txt", V[iStep,:],fmt="%.6f")
                np.savetxt(f"{download_path}/S_step_{iStep:03}.txt", S[iStep,:],fmt="%.0f")

          # import matplotlib.pyplot as plt
          # plt.figure(figsize=(12, 4.5))
          # indices = np.arange(nStep)
          # ts = indices * bm.get_dt()
          # plt.subplot(121)
          # bp.visualize.raster_plot(ts, E_sps, show=False)
          # plt.subplot(122)
          # bp.visualize.raster_plot(ts, I_sps, show=True)
          # plt.savefig("tmp")




