
from __future__ import unicode_literals

import six.moves
import numpy as np
import itertools

VITERBI_CONSTRAINT_NONE = 0
VITERBI_CONSTRAINT_FORBIDDEN = 1
VITERBI_CONSTRAINT_MANDATORY = 2



def pred2logemission(pred, eps=1e-10):
    pred = np.array(pred)
    ret = np.ones((len(pred), 2)) * eps
    ret[pred == 0, 0] = 1 - eps
    ret[pred == 1, 1] = 1 - eps
    return np.log(ret)

def log_trans_exp(exp,cost0=0, cost1=0):
    # transition cost is assumed to be 10**-exp
    cost = -exp * np.log(10)
    ret = np.ones((2,2)) * cost
    ret[0,0]= cost0
    ret[1,1]= cost1
    return ret

def diag_trans_exp(exp, dim):
    cost = -exp * np.log(10)
    ret = np.ones((dim, dim)) * cost
    for i in range(dim):
        ret[i, i] = 0
    return ret


LOG_ZERO = np.log(1e-200)

# handling 'consecutive' constraints is achieved by duplicating states
# the following functions are here to help in this process


# create new transition prob. matrix accounting for duplicated states.
def _update_transition(transition, consecutive):

    # initialize with LOG_ZERO everywhere
    # except on the +1 diagonal np.log(1)
    new_n_states = np.sum(consecutive)
    new_transition = LOG_ZERO * np.ones((new_n_states, new_n_states))
    for i in range(1, new_n_states):
        new_transition[i - 1, i] = np.log(1)

    n_states = len(consecutive)
    boundary = np.hstack(([0], np.cumsum(consecutive)))
    start = boundary[:-1]
    end = boundary[1:] - 1

    for i, j in itertools.product(six.moves.range(n_states), repeat=2):
        new_transition[end[i], start[j]] = transition[i, j]

    return new_transition


# create new initial prob. matrix accounting for duplicated states.
def _update_initial(initial, consecutive):

    new_n_states = np.sum(consecutive)
    new_initial = LOG_ZERO * np.ones((new_n_states, ))

    n_states = len(consecutive)
    boundary = np.hstack(([0], np.cumsum(consecutive)))
    start = boundary[:-1]

    for i in range(n_states):
        new_initial[start[i]] = initial[i]

    return new_initial


# create new emission prob. matrix accounting for duplicated states.
def _update_emission(emission, consecutive):

    return np.vstack(
        np.tile(e, (c, 1))  # duplicate emission probabilities c times
        for e, c in six.moves.zip(emission.T, consecutive)
    ).T


# create new constraint matrix accounting for duplicated states
def _update_constraint(constraint, consecutive):

    return np.vstack(
        np.tile(e, (c, 1))  # duplicate constraint probabilities c times
        for e, c in six.moves.zip(constraint.T, consecutive)
    ).T


# convert sequence of duplicated states back to sequence of original states.
def _update_states(states, consecutive):

    boundary = np.hstack(([0], np.cumsum(consecutive)))
    start = boundary[:-1]
    end = boundary[1:]

    new_states = np.empty(states.shape)

    for i, (s, e) in enumerate(six.moves.zip(start, end)):
        new_states[np.where((s <= states) & (states < e))] = i

    return new_states


def viterbi_decoding(emission, transition,
                     initial=None, consecutive=None, constraint=None):
    """(Constrained) Viterbi decoding

    Parameters
    ----------
    emission : array of shape (n_samples, n_states)
        E[t, i] is the emission log-probabilities of sample t at state i.
    transition : array of shape (n_states, n_states)
        T[i, j] is the transition log-probabilities from state i to state j.
    initial : optional, array of shape (n_states, )
        I[i] is the initial log-probabilities of state i.
        Defaults to equal log-probabilities.
    consecutive : optional, int or int array of shape (n_states, )
        C[i] is a the minimum-consecutive-states constraint for state i.
        C[i] = 1 is equivalent to no constraint (default).
    constraint : optional, array of shape (n_samples, n_states)
        K[t, i] = 1 forbids state i at time t.
        K[t, i] = 2 forces state i at time t.
        Use K[t, i] = 0 for no constraint (default).

    Returns
    -------
    states : array of shape (n_samples, )
        Most probable state sequence

    """

    # ~~ INITIALIZATION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    T, k = emission.shape  # number of observations x number of states

    # no minimum-consecutive-states constraints
    if consecutive is None:
        consecutive = np.ones((k, ), dtype=int)

    # same value for all states
    elif isinstance(consecutive, int):
        consecutive = consecutive * np.ones((k, ), dtype=int)

    # (potentially) different values per state
    else:
        consecutive = np.array(consecutive, dtype=int).reshape((k, ))

    # at least one sample
    consecutive = np.maximum(1, consecutive)

    # balance initial probabilities when they are not provided
    if initial is None:
        initial = np.log(np.ones((k, )) / k)

    # no constraint?
    if constraint is None:
        constraint = VITERBI_CONSTRAINT_NONE * np.ones((T, k))

    # artificially create new states to account for 'consecutive' constraints
    emission = _update_emission(emission, consecutive)
    transition = _update_transition(transition, consecutive)
    initial = _update_initial(initial, consecutive)
    constraint = _update_constraint(constraint, consecutive)
    T, K = emission.shape  # number of observations x number of new states
    states = np.arange(K)  # states 0 to K-1

    # set emission probability to zero for forbidden states
    emission[
        np.where(constraint == VITERBI_CONSTRAINT_FORBIDDEN)] = LOG_ZERO

    # set emission probability to zero for all states but the mandatory one
    for t, k in six.moves.zip(
        *np.where(constraint == VITERBI_CONSTRAINT_MANDATORY)
    ):
        emission[t, states != k] = LOG_ZERO

    # ~~ FORWARD PASS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    V = np.empty((T, K))                # V[t, k] is the probability of the
    V[0, :] = emission[0, :] + initial  # most probable state sequence for the
                                        # first t observations that has k as
                                        # its final state.

    P = np.empty((T, K), dtype=int)  # P[t, k] remembers which state was used
    P[0, :] = states                 # to get from time t-1 to time t at
                                     # state k

    for t in range(1, T):

        # tmp[k, k'] is the probability of the most probable path
        # leading to state k at time t - 1, plus the probability of
        # transitioning from state k to state k' (at time t)
        tmp = (V[t - 1, :] + transition.T).T

        # optimal path to state k at t comes from state P[t, k] at t - 1
        # (find among all possible states at this time t)
        P[t, :] = np.argmax(tmp, axis=0)

        # update V for time t
        V[t, :] = emission[t, :] + tmp[P[t, :], states]

    # ~~ BACK-TRACKING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    X = np.empty((T,), dtype=int)
    X[-1] = np.argmax(V[-1, :])
    for t in range(1, T):
        X[-(t + 1)] = P[-t, X[-t]]

    # ~~ CONVERT BACK TO ORIGINAL STATES

    return _update_states(X, consecutive)


def _energy_activity(loge, ratio=0.4):   ##########0.9

    threshold = np.mean(loge[np.isfinite(loge)]) + np.log(ratio)
    raw_activity = (loge > threshold)
    return viterbi_decoding(pred2logemission(raw_activity),
                            log_trans_exp(50, cost0=-5))
                            

def _binidx2seglist(binidx):
    """
    ss._binidx2seglist((['f'] * 5) + (['bbb'] * 10) + ['v'] * 5)
    Out: [('f', 0, 5), ('bbb', 5, 15), ('v', 15, 20)]
    
    #TODO: is there a pandas alternative??
    """
    curlabel = None
    bseg = -1
    ret = []
    for i, e in enumerate(binidx):
        if e != curlabel:
            if curlabel is not None:
                ret.append((curlabel, bseg, i))
            curlabel = e
            bseg = i
    ret.append((curlabel, bseg, i + 1))
    return ret



def framing(sig, win_size, win_shift=1, context=(0, 0), pad='zeros'):
    """
    :param sig: input signal, can be mono or multi dimensional
    :param win_size: size of the window in term of samples
    :param win_shift: shift of the sliding window in terme of samples
    :param context: tuple of left and right context
    :param pad: can be zeros or edge
    """
    dsize = sig.dtype.itemsize
    if sig.ndim == 1:
        sig = sig[:, np.newaxis]
    # Manage padding
    c = (context, ) + (sig.ndim - 1) * ((0, 0), )
    _win_size = win_size + sum(context)
    shape = (int((sig.shape[0] - win_size) / win_shift) + 1, 1, _win_size, sig.shape[1])
    strides = tuple(map(lambda x: x * dsize, [win_shift * sig.shape[1], 1, sig.shape[1], 1]))
    if pad == 'zeros':
        return np.lib.stride_tricks.as_strided(np.lib.pad(sig, c, 'constant', constant_values=(0,)),
                                                  shape=shape,
                                                  strides=strides).squeeze()
    elif pad == 'edge':
        return np.lib.stride_tricks.as_strided(np.lib.pad(sig, c, 'edge'),
                                                  shape=shape,
                                                  strides=strides).squeeze()


def pre_emphasis(input_sig, pre):
    """Pre-emphasis of an audio signal.
    :param input_sig: the input vector of signal to pre emphasize
    :param pre: value that defines the pre-emphasis filter. 
    """
    if input_sig.ndim == 1:
        return (input_sig - np.c_[input_sig[np.newaxis, :][..., :1],
                                     input_sig[np.newaxis, :][..., :-1]].squeeze() * pre)
    else:
        return input_sig - np.c_[input_sig[..., :1], input_sig[..., :-1]] * pre



def getfea(input_sig): 
   win_time=0.025
   fs=16000
   shift=0.01
   prefac=0.97
   window_length = int(round(win_time * fs))
   overlap = window_length - int(shift * fs)
   framed = framing(input_sig, window_length, win_shift=window_length-overlap).copy()
   framed = pre_emphasis(framed, prefac)
   log_energy = np.log((framed**2).sum(axis=1))
   return log_energy

def vad_timing_out(wav): 
  loge = getfea(wav) 
  vadseg=[]
  for lab, start, stop in _binidx2seglist(_energy_activity(loge)[::2]):
      if lab == 1:
          vadseg.append((start*0.02, stop*0.02))
  return vadseg                        
  
def vad_time_out(wav): 
  loge = getfea(wav) 
  x=0
  for lab, start, stop in _binidx2seglist(_energy_activity(loge)[::2]):
      if lab == 1:
          x = x + ((stop - start)*0.02)
  return x 