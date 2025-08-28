from brainpy._src.integrators import odeint
from typing import Union, Callable, Optional, Sequence
from brainpy.synapses import Exponential
from brainpy.types import ArrayType
from brainpy._src.dynsys import DynamicalSystem
from brainpy._src.dyn.base import SynDyn
from brainpy._src.integrators.ode.generic import odeint
from brainpy._src.mixin import AlignPost
from brainpy._src.context import share
from brainpy._src.dyn.neurons import lif

import warnings
import brainpy as bp
import numpy as np
import brainpy.math as bm
from typing import Callable
from pathlib import Path
import pickle
from bpusdk.BrainpyLib.BrainpyBase import BrainpyBase
import time

warnings.filterwarnings('ignore')

# eqvivalent to bp.dyn.LifRef
class LifRef(lif.LifRefLTC):
  def derivative(self, V, t, I):
    return (-V + self.V_rest + self.R * I) / self.tau

  def update(self, x=None):
    #self.integral = odeint(method=method, f=self.derivative,show_code=True)

    #------------LifRef(LifRefLTC)------------
    x = 0. if x is None else x
    x = self.sum_current_inputs(self.V.value, init=x)
    #return super().update(x)

    #-----------LifRefLTC(LifLTC)-----------
    t = share.load('t')
    dt = share.load('dt')

    # integrate membrane potential
  
    V = self.integral(self.V.value, t, x, dt) + self.sum_delta_inputs()
    #V = self.V.value + 2. + x
    #V =  lif_generated_function_dt1(self.size, self.V_rest,self.tau, x, self.V.value, jax.numpy.ones(self.size, jax.numpy.float32)*dt) + self.sum_delta_inputs()
    #V = lif_generated_function_ori(self.size, x, self.V.value, jax.numpy.ones(self.size, jax.numpy.float32)*dt) + self.sum_delta_inputs()
    
    
    #V = self.V.value - (np.exp(-1/self.tau) - 1)*(self.V_rest - self.V.value + x) + self.sum_delta_inputs()
    
    # refractory
    refractory = (t - self.t_last_spike) <= self.tau_ref
    V = bm.where(refractory, self.V.value, V)

    spike = V > self.V_th
    V = bm.where(spike, self.V_reset, V)
    # if self.ref_var:
    #   self.refractory.value = bm.logical_or(refractory, spike)
    t_last_spike = bm.where(spike, t, self.t_last_spike.value)

    self.V.value = V
    self.spike.value = spike
    self.t_last_spike.value = t_last_spike
    return spike
  
#eqvivalant with bp.dyn.Expon
class ConstantExpon(SynDyn, AlignPost):
  def __init__(
      self,
      size: Union[int, Sequence[int]],
      keep_size: bool = False,
      sharding: Optional[Sequence[str]] = None,
      method: str = 'exp_auto',
      name: Optional[str] = None,
      mode: Optional[bm.Mode] = None,

      # synapse parameters
      tau: Union[float, ArrayType, Callable] = 8.0,
  ):
    super().__init__(name=name,
                     mode=mode,
                     size=size,
                     keep_size=keep_size,
                     sharding=sharding)

    # parameters
    self.tau = self.init_param(tau)

    # functionodeint
    self.integral = odeint(self.derivative, method=method,show_code=False)
    self._current = None

    self.reset_state(self.mode)

  def derivative(self, g, t):
    return -g / self.tau

  def reset_state(self, batch_or_mode=None, **kwargs):
    self.g = self.init_variable(bm.zeros, batch_or_mode)

  def update(self, x=None):
    #self.integral.showcode = True
    #self.g.value = self.integral(self.g.value, share['t'], share['dt'])
    self.g.value = self.g.value

    if x is not None:
      self.add_current(x)
    return self.g.value

  def add_current(self, x):
    self.g.value += x

  def return_info(self):
    return self.g

    
class Exponential(bp.Projection): 
  def __init__(self, nNeuron, pre, post, delay, prob, g_max, tau, E, method,allow_multi_conn):
    super().__init__()
    conn = self.createConn(nNeuron,prob, pre, post,allow_multi_conn)
    self.pron = bp.dyn.FullProjAlignPost(
      pre=pre,
      delay=delay,
      # Event-driven computation
      comm=bp.dnn.EventCSRLinear(conn, g_max), 
      syn=ConstantExpon(size=post.num, tau=tau,method=method),
      out=bp.dyn.CUBA(), # COBA network
      post=post
    )

  def createConn_by_prepost(self, nNeuron, prob, pre, post, allow_multi_conn):
      pre_list_ori,post_list_ori = prob
      ii_pre = np.where(pre_list_ori<nNeuron[0]) if pre.name[-1] == '0' else np.where(pre_list_ori>=nNeuron[0])
      ii_post = np.where(post_list_ori<nNeuron[0]) if post.name[-1] == '0' else np.where(post_list_ori>=nNeuron[0])
      ii = set(ii_pre[0]) & set(ii_post[0])
      ii = np.array(list(ii))

      if len(ii) == 0:
          conn = bp.conn.FixedProb(0, pre=pre.num, post=post.num, allow_multi_conn=True) 
      
      else:
          pre_list = pre_list_ori[ii]
          offset_pre = 0 if pre.name[-1] == '0' else nNeuron[0]
          pre_list -= offset_pre

          post_list = post_list_ori[ii]
          offset_post = 0 if post.name[-1] == '0' else nNeuron[0]
          post_list -= offset_post

          conn = bp.conn.IJConn(i=pre_list, j=post_list)
          conn = conn(pre_size=pre.num, post_size=post.num)
      return conn
  
  def createConn(self, nNeuron, conn, pre, post, allow_multi_conn):
      match conn[0]:
          case 'customized':
              conn = self.createConn_by_prepost(nNeuron, conn[1], pre, post, allow_multi_conn)
          case 'FixedPreNum':
              conn = bp.conn.FixedPreNum(conn[1], pre=pre.num, post=post.num, allow_multi_conn=allow_multi_conn)
          case 'FixedPostNum':
              conn = bp.conn.FixedPostNum(conn[1], pre=pre.num, post=post.num, allow_multi_conn=allow_multi_conn)
          case 'FixedTotalNum':
              conn = bp.conn.FixedTotalNum(conn[1], pre=pre.num, post=post.num, allow_multi_conn=allow_multi_conn)
          case 'FixedProb':
              conn = bp.conn.FixedProb(conn[1], pre=pre.num, post=post.num, allow_multi_conn=allow_multi_conn)
          case 'FixedPostNum':
              conn = bp.conn.FixedPostNum(conn[1], pre=pre.num, post=post.num, allow_multi_conn=allow_multi_conn)
          case _:
              print(f"conn is of unsopported type")     
      return conn
  
  def update(self, *args, **kwargs):
    nodes = tuple(self.nodes(level=1, include_self=False).subset(DynamicalSystem).unique().values())
    if len(nodes):
      for node in nodes:
        node.update(*args, **kwargs)
    else:
      raise ValueError('Do not implement the update() function.')
  
class EINet(bp.DynamicalSystem):
    def __init__(self, ne, ni, conn, method, allow_multi_conn=True):
        super().__init__()
        self.initState = bm.random.DEFAULT.value
        self.neuron_scale = [ne, ni]
        tauRef = 0+0.0001 # Make sure tauRef always == 5 timesteps 
        self.E = bp.dyn.LifRef(ne, V_rest=2., V_th=20., V_reset=2., tau=1, tau_ref=tauRef,
                               V_initializer=bp.init.Uniform(-40.,18),method=method)
        self.I = bp.dyn.LifRef(ni, V_rest=2., V_th=20., V_reset=2., tau=1, tau_ref=tauRef,
                               V_initializer=bp.init.Uniform(-40.,18),method=method)

        # padding = np.zeros(ne)
        # padding[4092] = -10
        # self.E.V.value += padding

        self.E.V.value = np.floor(self.E.V.value)
        self.I.V.value = np.floor(self.I.V.value)

        self.E2E = Exponential(self.neuron_scale, self.E, self.E, delay=0.,
                               prob=conn, g_max=2, tau=1., E=1.,method=method,allow_multi_conn=allow_multi_conn)
        self.E2I = Exponential(self.neuron_scale, self.E, self.I, delay=0.,
                               prob=conn, g_max=2, tau=1., E=1.,method=method,allow_multi_conn=allow_multi_conn)

        self.I2E = Exponential(self.neuron_scale, self.I, self.E, delay=0.,
                               prob=conn, g_max=2, tau=1., E=1.,method=method,allow_multi_conn=allow_multi_conn)
        self.I2I = Exponential(self.neuron_scale, self.I, self.I, delay=0.,
                               prob=conn, g_max=2, tau=1., E=1.,method=method,allow_multi_conn=allow_multi_conn)
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

    def dump(self,download_path,inpS,inpE,nStep,jit=True,save=True, txt=False): 
        V_init = np.concatenate((self.E.V.value, self.I.V.value), axis=0)
        V_init = np.expand_dims(V_init, axis=0)
        S_init = np.zeros((1, self.ne+self.ni))
        wacc_init = np.zeros((1, self.ne+self.ni))
    
        start = time.time()
        runner = bp.DSRunner(
            self, monitors=['E.spike', 'I.spike', 'E.V', 'I.V','E2E.pron.syn.g','E2I.pron.syn.g','I2E.pron.syn.g','I2I.pron.syn.g'], jit=jit)
        _ = runner.run(inputs=[inpS, bm.ones(nStep) * inpE])
        end = time.time()
        print(f"AVG_sim_time_per_step: {(end-start)/nStep*1000:.2f} ms")
        
        E_sps = runner.mon['E.spike']
        I_sps = runner.mon['I.spike']
        E_V = runner.mon['E.V']
        I_V = runner.mon['I.V']
        E2E = runner.mon['E2E.pron.syn.g']
        E2I = runner.mon['E2I.pron.syn.g']
        I2E = runner.mon['I2E.pron.syn.g']
        I2I = runner.mon['I2I.pron.syn.g']

        S = np.concatenate((E_sps, I_sps), axis=1)
        S = np.concatenate((S_init, S), axis=0)
        V = np.concatenate((E_V, I_V), axis=1)
        V = np.concatenate((V_init, V), axis=0)
        #Do not need to scale as g keep constant between steps
        wacc1 = np.concatenate((E2E, E2I), axis=1)
        wacc1 = np.concatenate((wacc_init, wacc1), axis=0)
        wacc2 = np.concatenate((I2E, I2I), axis=1)
        wacc2 = np.concatenate((wacc_init, wacc2), axis=0)

        if save == True:
          download_path = f"{download_path}/soft_data"
          download_dir = Path(download_path)
          download_dir.mkdir(exist_ok=True,parents=True)
          np.save(download_dir / "N_V.npy", V)
          np.save(download_dir / "N_spike.npy", S)
          np.save(download_dir / "N_wacc1.npy", wacc1+wacc2)
          np.save(download_dir / "N_wacc2.npy", np.zeros((nStep+1, self.ne+self.ni)))
          
          test = BrainpyBase(self, inpE,{})
          conn_matrix = test.get_connection_matrix()
          cv = test.cv
          with open(f'{download_dir}/connection.pickle', 'wb') as handle:
              pickle.dump(conn_matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

        else:
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




