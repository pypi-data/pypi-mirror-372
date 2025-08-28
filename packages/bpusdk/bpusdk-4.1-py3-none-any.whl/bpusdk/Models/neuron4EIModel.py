import random
import warnings
from pathlib import Path

import brainpy as bp
import jax
import numpy as np
from brainpy import math as bm
from brainpy._src.initialize import noise as init_noise
import pickle
from bpusdk.BrainpyLib.BrainpyBase import BrainpyBase

warnings.filterwarnings('ignore')

class Exponential_ori(bp.Projection):
    def __init__(self, pre, post, delay, prob, g_max, tau, E, method, allow_multi_conn):
        super().__init__()
        self.pron = bp.dyn.FullProjAlignPost(
            pre=pre,
            delay=delay,
            comm=bp.dnn.EventCSRLinear(bp.conn.FixedProb(prob, pre=pre.num, post=post.num, seed=42, allow_multi_conn=allow_multi_conn), g_max),
            syn=bp.dyn.Expon(size=post.num, tau=tau,method=method),  
            out=bp.dyn.COBA(E = E),  
            post=post
        )

class Exponential(bp.Projection):
    def __init__(self, pre, post, delay, prob, g_max, tau, E, method, allow_multi_conn):
        super().__init__()
        conn = self.createConn(prob, pre, post,allow_multi_conn)
        self.pron = bp.dyn.FullProjAlignPost(
            pre=pre,
            delay=delay,
            comm=bp.dnn.EventCSRLinear(conn, g_max),
            syn=bp.dyn.Expon(size=post.num, tau=tau,method=method),  # Exponential synapse
            out=bp.dyn.COBA(E=E),  # COBA network
            post=post
        )
    
    def createConn_by_prop(self, prob, pre, post, allow_multi_conn):
        conn = bp.conn.FixedProb(prob, pre=pre.num, post=post.num, seed=42, allow_multi_conn=allow_multi_conn)
        return conn

    def createConn_by_fanout(self):
        1

    def createConn_by_prepost(self, prob, pre, post, allow_multi_conn):
        pre_list_ori,post_list_ori = prob
        ii_pre = np.where(pre_list_ori<pre.num) if pre.name[-1] == '0' else np.where(pre_list_ori>=pre.num)
        ii_post = np.where(post_list_ori<pre.num) if post.name[-1] == '0' else np.where(post_list_ori>=pre.num)
        ii = set(ii_pre[0]) & set(ii_post[0])
        ii = np.array(list(ii))

        pre_list = pre_list_ori[ii]
        offset_pre = 0 if pre.name[-1] == '0' else pre.num
        pre_list -= offset_pre

        post_list = post_list_ori[ii]
        offset_post = 0 if post.name[-1] == '0' else pre.num
        post_list -= offset_post

        conn = bp.conn.IJConn(i=pre_list, j=post_list)
        conn = conn(pre_size=pre.num, post_size=post.num)
        return conn

    def createConn(self, prob, pre, post, allow_multi_conn):
        if isinstance(prob, float) and 0 <= prob <= 1:
            conn = self.createConn_by_prop(prob, pre, post, allow_multi_conn)
            print(f"conn = {conn} is a float and within the range 0 to 0.1")
        
        elif isinstance(prob, np.ndarray):
            conn = self.createConn_by_prepost(prob, pre, post, allow_multi_conn)

        else:
            print(f"conn is of unsopported type")         
        return conn


class EINet(bp.DynamicalSystem):
    def __init__(self, ne, ni, connect_prob, method, allow_multi_conn, neuron_type = "LIF"):
        super().__init__()
        self.neuron_scale = 0.5
        tauRef = bm.get_dt()*5.+0.0001 # Make sure tauRef always == 5 timesteps 
        
        if neuron_type == "LIF":
            self.E = bp.dyn.LifRef(ne, V_rest=-60., V_th=-50., V_reset=-60., tau=20., tau_ref=tauRef,
                                V_initializer=bp.init.Normal(-55., 2.),method=method)
            self.I = bp.dyn.LifRef(ni, V_rest=-60., V_th=-50., V_reset=-60., tau=20., tau_ref=tauRef,
                                V_initializer=bp.init.Normal(-55., 2.),method=method)
        elif neuron_type == "Izhikevich":
            self.E = bp.dyn.IzhikevichRef(ne, tau_ref=tauRef, V_initializer=bp.init.Uniform(-100.,-15), method=method)
            self.I = bp.dyn.IzhikevichRef(ni, tau_ref=tauRef, V_initializer=bp.init.Uniform(-100.,-15), method=method)
        
        # module = __import__('brainpy.dyn.neurons', fromlist=[''])
        # cls = get_class(module, neuron_type)
        
        # self.E = cls(ne, V_rest=-60., V_th=-50., V_reset=-60., tau=20., tau_ref=tauRef,
        #                        V_initializer=bp.init.Normal(-55., 2.),method=method)
        # self.I = cls(ni, V_rest=-60., V_th=-50., V_reset=-60., tau=20., tau_ref=tauRef,
        #                        V_initializer=bp.init.Normal(-55., 2.),method=method)
        
        # self.E = bp.dyn.LifRef(ne, V_rest=-60., V_th=-50., V_reset=-60., tau=20., tau_ref=tauRef,
        #                        V_initializer=bp.init.Normal(-55., 2.),method=method)
        # self.I = bp.dyn.LifRef(ni, V_rest=-60., V_th=-50., V_reset=-60., tau=20., tau_ref=tauRef,
        #                        V_initializer=bp.init.Normal(-55., 2.),method=method)

        self.E2E = Exponential(self.E, self.E, delay=0.,
                               prob=connect_prob, g_max=0.6, tau=5., E=0.,method=method,allow_multi_conn=allow_multi_conn)
        self.E2I = Exponential(self.E, self.I, delay=0.,
                               prob=connect_prob, g_max=0.6, tau=5., E=0.,method=method,allow_multi_conn=allow_multi_conn)
        self.I2E = Exponential(self.I, self.E, delay=0.,
                               prob=connect_prob, g_max=6.7, tau=10., E=-80.,method=method,allow_multi_conn=allow_multi_conn)
        self.I2I = Exponential(self.I, self.I, delay=0.,
                               prob=connect_prob, g_max=6.7, tau=10., E=-80.,method=method,allow_multi_conn=allow_multi_conn)
        self.ne = ne
        self.ni = ni

    def update(self, inpS, inpE):
        inpS = inpS.astype(bool)
        self.E2E.pron.refs['pre'].spike.value += inpS[:self.ne]
        self.E2I.pron.refs['pre'].spike.value += inpS[:self.ne]
        self.I2E.pron.refs['pre'].spike.value += inpS[self.ni:]
        self.I2I.pron.refs['pre'].spike.value += inpS[self.ni:]

        self.E2E()
        self.E2I()
        self.I2E()
        self.I2I()
        self.E(inpE)
        self.I(inpE)
        # monitor
        return self.E.spike, self.I.spike

    def dump(self,download_path,inpS,inpE,nStep,jit=True): 
        runner = bp.DSRunner(
            self, monitors=['E.spike', 'I.spike', 'E.V', 'I.V','E2E.pron.syn.g','E2I.pron.syn.g','I2E.pron.syn.g','I2I.pron.syn.g'], jit=jit)
        _ = runner.run(inputs=[inpS, bm.ones(nStep) * inpE])
        E_sps = runner.mon['E.spike']
        I_sps = runner.mon['I.spike']
        E_V = runner.mon['E.V']
        I_V = runner.mon['I.V']
        E2E = runner.mon['E2E.pron.syn.g']
        E2I = runner.mon['E2I.pron.syn.g']
        I2E = runner.mon['I2E.pron.syn.g']
        I2I = runner.mon['I2I.pron.syn.g']

        S = np.concatenate((E_sps, I_sps), axis=1)
        V = np.concatenate((E_V, I_V), axis=1)
        wacc1 = np.concatenate((I2E, I2I), axis=1)
        wacc2 = np.concatenate((E2E, E2I), axis=1)

        download_path = f"{download_path}/soft_data"
        download_dir = Path(download_path)
        download_dir.mkdir(exist_ok=True,parents=True)
        np.save(download_dir / "N_V.npy", V)
        np.save(download_dir / "N_spike.npy", S)
        np.save(download_dir / "N_wacc1.npy", wacc1)
        np.save(download_dir / "N_wacc2.npy", wacc2)
        
        test = BrainpyBase(self, inpE)
        conn_matrix = test.get_connection_matrix()
        cv = test.cv
        with open(f'{download_dir}/connection.pickle', 'wb') as handle:
            pickle.dump(conn_matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

        download_path = f"{download_path}/soft_data/ref_data"
        download_dir = Path(download_path)
        download_dir.mkdir(exist_ok=True,parents=True)
        for iStep in range(nStep):
            path = f"{download_path}/soft_data/ref_data/{iStep}"
            data = V[iStep,:]
            np.savetxt('output.csv', data, delimiter=',', fmt='%d')
            
        

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    random.seed(1)
    bm.random.seed(42)
    bm.set_dt(0.1)
        
    # Scope paramter
    scope = 96
    nNeuron = scope*1024
    nExc = int(nNeuron/2)
    nInh = int(nNeuron/2)
    nNeuron = nExc+nInh
    connect_prob = 5 / nNeuron
    #connect_prob = np.load("W:\int8\Gdiist-BPU-Toolkit\conn_info.npy")

    net = EINet(nExc, nInh,connect_prob,method = "euler", allow_multi_conn= True)


    # Simulation parameter 
    nStep = 100
    inpE = 15.                                       # Constant current stimuli injected to all neurons during all steps 
    inpS = np.zeros((nStep, nNeuron))
    spk_ranges = 1.6
    key = jax.random.PRNGKey(1)
    x = bm.where(jax.random.normal(key, shape=(
        min(16384, nNeuron),)) >= spk_ranges, 1, 0)
    inpS[0][:16384] = x 
    inpS = inpS.astype(bool)

    # bp.integrators.compile_integrators(net.step_run, 0, 0.)
    # for intg in net.nodes().subset(bp.Integrator).values():
    #   print(intg.to_math_expr())

    # Alt1 
    runner = bp.DSRunner(net, monitors=['E.spike', 'I.spike', 'E.V', 'I.V','E2E.pron.syn.g','E2I.pron.syn.g','I2E.pron.syn.g','I2I.pron.syn.g'], jit=False)
    _ = runner.run(inputs= [inpS,bm.ones(nStep) * inpE])
    E_sps = runner.mon['E.spike']
    I_sps = runner.mon['I.spike']
    E_V = runner.mon['E.V']
    I_V = runner.mon['I.V']
    E2E = runner.mon['E2E.pron.syn.g']
    E2I = runner.mon['E2I.pron.syn.g']
    I2E = runner.mon['I2E.pron.syn.g']
    I2I = runner.mon['I2I.pron.syn.g']

    # s = np.concatenate((E_sps, I_sps), axis=1)
    # V = np.concatenate((E_V, I_V), axis=1)
    # wacc1 = np.concatenate((I2E, I2I), axis=1)
    # wacc2 = np.concatenate((E2E, E2I), axis=1)

    # download_dir = Path('./tmp96_new/soft_data')
    # download_dir.mkdir(exist_ok=True,parents=True)
    # np.save(download_dir / "N_V.npy", V)
    # np.save(download_dir / "N_spike.npy", s)
    # np.save(download_dir / "N_wacc1.npy", wacc1)
    # np.save(download_dir / "N_wacc2.npy", wacc2)

    
    test = BrainpyBase(net, inpE)
    conn_matrix = test.get_connection_matrix()
    cv = test.cv
    # with open('./tmp96_new/soft_data/connection.pickle', 'wb') as handle:
    #     pickle.dump(conn_matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Alt 2
    # def run_fun(i):
    #   return net.step_run(i, inpE)
    # indices = np.arange(total_step)  # arange by step
    # E_sps, I_sps = bm.for_loop(run_fun, indices)
    # E_sps = E_sps.value
    # I_sps = I_sps.value

    # Print
    data = np.sum(E_sps, axis=1) + np.sum(I_sps, axis=1)
    print(data)

    # Vis
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 4.5))
    indices = np.arange(nStep)
    ts = indices * bm.get_dt()
    plt.subplot(121)
    bp.visualize.raster_plot(ts, E_sps, show=False)
    plt.subplot(122)
    bp.visualize.raster_plot(ts, I_sps, show=True)
    plt.savefig("tmp")
