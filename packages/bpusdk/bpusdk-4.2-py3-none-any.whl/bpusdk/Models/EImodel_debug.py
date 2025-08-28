from brainpy.synapses import Exponential
from typing import Union, Callable, Optional, Any, Sequence
from brainpy._src.dyn.neurons import lif
from brainpy.types import ArrayType
from brainpy._src.dyn.base import SynDyn
from brainpy._src.integrators.ode.generic import odeint
from brainpy._src.mixin import AlignPost, ReturnInfo
from brainpy._src.delay import (delay_identifier,
                                register_delay_by_return)
from brainpy._src.dynsys import DynamicalSystem, Projection
from brainpy._src.mixin import (JointType, ParamDescriber, SupportAutoDelay, BindCondData, AlignPost)
from brainpy._src.context import share

import warnings
import brainpy as bp
from brainpy import math as bm, check
import numpy as np
from pathlib import Path
import pickle
from bpusdk.BrainpyLib.BrainpyBase import BrainpyBase

warnings.filterwarnings('ignore')

class myFullProjAlignPost(Projection):
  def __init__(
      self,
      pre: JointType[DynamicalSystem, SupportAutoDelay],
      delay: Union[None, int, float],
      comm: DynamicalSystem,
      syn: JointType[DynamicalSystem, AlignPost],
      out: JointType[DynamicalSystem, BindCondData],
      post: DynamicalSystem,
      out_label: Optional[str] = None,
      name: Optional[str] = None,
      mode: Optional[bm.Mode] = None,
  ):
    super().__init__(name=name, mode=mode)

    # synaptic models
    check.is_instance(pre, JointType[DynamicalSystem, SupportAutoDelay])
    check.is_instance(comm, DynamicalSystem)
    check.is_instance(syn, JointType[DynamicalSystem, AlignPost])
    check.is_instance(out, JointType[DynamicalSystem, BindCondData])
    check.is_instance(post, DynamicalSystem)
    self.comm = comm
    self.syn = syn

    # delay initialization
    delay_cls = register_delay_by_return(pre)
    delay_cls.register_entry(self.name, delay)

    # synapse and output initialization
    post.add_inp_fun(self.name, out, label=out_label)

    # references
    self.refs = dict()
    # invisible to ``self.nodes()``
    self.refs['pre'] = pre
    self.refs['post'] = post
    self.refs['out'] = out
    # unify the access
    self.refs['delay'] = delay_cls
    self.refs['comm'] = comm
    self.refs['syn'] = syn

  def update(self):
    x = self.refs['delay'].at(self.name)
    g = self.syn(self.comm(x))
    self.refs['out'].bind_cond(g)  # synapse post current
    return g

  delay = property(lambda self: self.refs['delay'])
  pre = property(lambda self: self.refs['pre'])
  post = property(lambda self: self.refs['post'])
  out = property(lambda self: self.refs['out'])


# eqvivalent with VV - (exp(-TT/tau) - 1)*(V_rest - VV + XX): XX, VV, TT = a, b, c
def lif_generated_function_dt1(shape, V_rest, tau, XX, VV, TT):
    dt = bm.get_dt()
    dV =  (V_rest-VV+XX)/tau
    Vnew = VV + dV* dt
    return Vnew

# eqvivalent with TT*exp(-GG/tau): GG,TT = a,b
def syn_generated_function_dt1(shape,tau,GG, TT):
    dt = bm.get_dt()
    dG = -GG/tau
    GG = GG + dG*dt
    return GG

#eqvivalent to bp.dyn.LifRef
class my_LifRef(lif.LifRefLTC):
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
    x = 0. if x is None else x

    # integrate membrane potential
  
    #V = self.integral(self.V.value, t, x, dt) + self.sum_delta_inputs()
    V = self.V.value + (self.V_rest-self.V.value+self.R*x) * dt/self.tau

    # refractory
    refractory = (t - self.t_last_spike) <= self.tau_ref
    # if isinstance(self.mode, bm.TrainingMode):
    #   refractory = stop_gradient(refractory)
    V = bm.where(refractory, self.V.value, V)

    # spike, refractory, spiking time, and membrane potential reset
    # if isinstance(self.mode, bm.TrainingMode):
    #   spike = self.spk_fun(V - self.V_th)
    #   spike_no_grad = stop_gradient(spike) if self.detach_spk else spike
    #   if self.spk_reset == 'soft':
    #     V -= (self.V_th - self.V_reset) * spike_no_grad
    #   elif self.spk_reset == 'hard':
    #     V += (self.V_reset - V) * spike_no_grad
    #   else:
    #     raise ValueError
    #   spike_ = spike_no_grad > 0.
    #   # will be used in other place, like Delta Synapse, so stop its gradient
    #   if self.ref_var:
    #     self.refractory.value = stop_gradient(bm.logical_or(refractory, spike_).value)
    #   t_last_spike = stop_gradient(bm.where(spike_, t, self.t_last_spike.value))

    # else:
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
class my_Expon(SynDyn, AlignPost):
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
    self.integral = odeint(self.derivative, method=method,show_code=True)
    self._current = None

    self.reset_state(self.mode)

  def derivative(self, g, t):
    return -g / self.tau

  def reset_state(self, batch_or_mode=None, **kwargs):
    self.g = self.init_variable(bm.zeros, batch_or_mode)

  def update(self, x=None):
    #self.integral.showcode = True
    self.g.value = self.integral(self.g.value, share['t'], share['dt'])
    #self.g.value = syn_generated_function_dt1(self.size, self.tau, self.g.value, jax.numpy.ones(self.size, jax.numpy.float32)*share.load('dt'))
    
    #self.g.value = syn_generated_function_ori(self.size, jax.numpy.ones(self.size, jax.numpy.float32)*share.load('dt'),self.g.value)
    
    #self.g.value = np.exp(-1/self.tau) * self.g.value 

    if x is not None:
      self.add_current(x)
    return self.g.value

  def add_current(self, x):
    self.g.value += x

  def return_info(self):
    return self.g

    
class Exponential(bp.Projection): 
  def __init__(self, pre, post, delay, prob, g_max, tau, E, method,allow_multi_conn):
    super().__init__()
    conn = self.createConn(prob, pre, post,allow_multi_conn)
    self.pron = myFullProjAlignPost(
      pre=pre,
      delay=delay,
      # Event-driven computation
      comm=bp.dnn.EventCSRLinear(conn, g_max), 
      syn=my_Expon(size=post.num, tau=tau,method=method),# Exponential synapse
      out=bp.dyn.COBA(E=E), # COBA network
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
      
      elif isinstance(prob, np.ndarray):
          conn = self.createConn_by_prepost(prob, pre, post, allow_multi_conn)

      else:
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
    def __init__(self, ne, ni, connect_prob, method, allow_multi_conn):
        super().__init__()
        self.neuron_scale = 0.5
        tauRef = 0+0.0001 
        self.E = my_LifRef(ne, V_rest=-60., V_th=-10., V_reset=-60., tau=20., tau_ref=tauRef,
                               V_initializer=bp.init.Uniform(-100.,-15),method=method)
        self.I = my_LifRef(ni, V_rest=-60., V_th=-10., V_reset=-60., tau=20., tau_ref=tauRef,
                               V_initializer=bp.init.Uniform(-100.,-15),method=method)

        self.E2E = Exponential(self.E, self.E, delay=0.,
                               prob=connect_prob, g_max=1, tau=5., E=0.,method=method,allow_multi_conn=allow_multi_conn)
        self.E2I = Exponential(self.E, self.I, delay=0.,
                               prob=connect_prob, g_max=1, tau=5., E=0.,method=method,allow_multi_conn=allow_multi_conn)
        self.ne = ne
        self.ni = ni

    def update(self, inpS, inpE):
        inpS = inpS.astype(bool)
        self.E2E.pron.refs['pre'].spike.value += inpS[:self.ne]
        self.E2I.pron.refs['pre'].spike.value += inpS[:self.ne]

        self.E2E()
        self.E2I()
        self.E(inpE)
        self.I(inpE)
        return self.E.spike, self.I.spike

    
    def dump(self,download_path,inpS,inpE,nStep,jit=True,save=True): 
        V_init = np.concatenate((self.E.V.value, self.I.V.value), axis=0)
        V_init = np.expand_dims(V_init, axis=0)
        S_init = np.zeros((1, self.ne+self.ni))
        wacc_init = np.zeros((1, self.ne+self.ni))
    
        runner = bp.DSRunner(
            self, monitors=['E.spike', 'I.spike', 'E.V', 'I.V','E2E.pron.syn.g','E2I.pron.syn.g'], jit=jit)
        _ = runner.run(inputs=[inpS, bm.ones(nStep) * inpE])
        E_sps = runner.mon['E.spike']
        I_sps = runner.mon['I.spike']
        E_V = runner.mon['E.V']
        I_V = runner.mon['I.V']
        E2E = runner.mon['E2E.pron.syn.g']
        E2I = runner.mon['E2I.pron.syn.g']
        # I2E = runner.mon['I2E.pron.syn.g']
        # I2I = runner.mon['I2I.pron.syn.g']

        S = np.concatenate((E_sps, I_sps), axis=1)
        S = np.concatenate((S_init, S), axis=0)
        V = np.concatenate((E_V, I_V), axis=1)
        V = np.concatenate((V_init, V), axis=0)
        # wacc1 = np.concatenate((I2E, I2I), axis=1)
        wacc2 = np.concatenate((E2E, E2I), axis=1)
        wacc2 = np.concatenate((wacc_init, wacc2), axis=0)

        if save == True:
          download_path = f"{download_path}/soft_data"
          download_dir = Path(download_path)
          download_dir.mkdir(exist_ok=True,parents=True)
          np.save(download_dir / "N_V.npy", V)
          np.save(download_dir / "N_spike.npy", S)
          # np.save(download_dir / "N_wacc1.npy", wacc1)
          np.save(download_dir / "N_wacc2.npy", wacc2)
          
          test = BrainpyBase(self, inpE)
          conn_matrix = test.get_connection_matrix()
          cv = test.cv
          with open(f'{download_dir}/connection.pickle', 'wb') as handle:
              pickle.dump(conn_matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

        else:
          S = np.sum(S,axis=1)
          print(S)
        
          # import matplotlib.pyplot as plt
          # plt.figure(figsize=(12, 4.5))
          # indices = np.arange(nStep)
          # ts = indices * bm.get_dt()
          # plt.subplot(121)
          # bp.visualize.raster_plot(ts, E_sps, show=False)
          # plt.subplot(122)
          # bp.visualize.raster_plot(ts, I_sps, show=True)
          # plt.savefig("tmp")