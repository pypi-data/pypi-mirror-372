import numpy as np
import six
import scipy
import scipy.fftpack as fft
from numpy.lib.stride_tricks import as_strided

MAX_MEM_BLOCK = 2**8 * 2**10

class LibrosaError(Exception):
    '''The root librosa exception class'''
    pass


class ParameterError(LibrosaError):
    '''Exception class for mal-formed inputs'''
    pass
 



def tiny(x):

    # Make sure we have an array view
    x = np.asarray(x)

    # Only floating types generate a tiny
    if np.issubdtype(x.dtype, np.floating) or np.issubdtype(
        x.dtype, np.complexfloating
    ):
        dtype = x.dtype
    else:
        dtype = np.float32

    return np.finfo(dtype).tiny



 
def expand_to(x, *, ndim, axes):
   

    # Force axes into a tuple

    try:
        axes = tuple(axes)
    except TypeError:
        axes = tuple([axes])

    if len(axes) != x.ndim:
        raise ParameterError(
            "Shape mismatch between axes={} and input x.shape={}".format(axes, x.shape)
        )

    if ndim < x.ndim:
        raise ParameterError(
            "Cannot expand x.shape={} to fewer dimensions ndim={}".format(x.shape, ndim)
        )

    shape = [1] * ndim
    for i, axi in enumerate(axes):
        shape[axi] = x.shape[i]

    return x.reshape(shape)



def fix_length(data, *, size, axis=-1, **kwargs):
    
    kwargs.setdefault("mode", "constant")

    n = data.shape[axis]

    if n > size:
        slices = [slice(None)] * data.ndim
        slices[axis] = slice(0, size)
        return data[tuple(slices)]

    elif n < size:
        lengths = [(0, 0)] * data.ndim
        lengths[axis] = (0, size - n)
        return np.pad(data, lengths, **kwargs)

    return data


    
def dtype_c2r(d, *, default=np.float32):
    mapping = {
        np.dtype(np.complex64): np.float32,
        np.dtype(np.complex128): np.float64,
        np.dtype(complex): np.dtype(np.float32).type,   
    }

    # If we're given a real type already, return it
    dt = np.dtype(d)
    if dt.kind == "f":
        return dt

    # Otherwise, try to map the dtype.
    # If no match is found, return the default.
    return np.dtype(mapping.get(np.dtype(d), default))    
def __overlap_add(y, ytmp, hop_length):
    # numba-accelerated overlap add for inverse stft
    # y is the pre-allocated output buffer
    # ytmp is the windowed inverse-stft frames
    # hop_length is the hop-length of the STFT analysis

    n_fft = ytmp.shape[-2]
    for frame in range(ytmp.shape[-1]):
        sample = frame * hop_length
        y[..., sample : (sample + n_fft)] += ytmp[..., frame]
        
  
def normalize(S, *, norm=np.inf, axis=0, threshold=None, fill=None):
   

    # Avoid div-by-zero
    if threshold is None:
        threshold = tiny(S)

    elif threshold <= 0:
        raise ParameterError(
            "threshold={} must be strictly " "positive".format(threshold)
        )

    if fill not in [None, False, True]:
        raise ParameterError("fill={} must be None or boolean".format(fill))

    if not np.all(np.isfinite(S)):
        raise ParameterError("Input must be finite")

    # All norms only depend on magnitude, let's do that first
    mag = np.abs(S).astype(float)

    # For max/min norms, filling with 1 works
    fill_norm = 1

    if norm == np.inf:
        length = np.max(mag, axis=axis, keepdims=True)

    elif norm == -np.inf:
        length = np.min(mag, axis=axis, keepdims=True)

    elif norm == 0:
        if fill is True:
            raise ParameterError("Cannot normalize with norm=0 and fill=True")

        length = np.sum(mag > 0, axis=axis, keepdims=True, dtype=mag.dtype)

    elif np.issubdtype(type(norm), np.number) and norm > 0:
        length = np.sum(mag ** norm, axis=axis, keepdims=True) ** (1.0 / norm)

        if axis is None:
            fill_norm = mag.size ** (-1.0 / norm)
        else:
            fill_norm = mag.shape[axis] ** (-1.0 / norm)

    elif norm is None:
        return S

    else:
        raise ParameterError("Unsupported norm: {}".format(repr(norm)))

    # indices where norm is below the threshold
    small_idx = length < threshold

    Snorm = np.empty_like(S)
    if fill is None:
        # Leave small indices un-normalized
        length[small_idx] = 1.0
        Snorm[:] = S / length

    elif fill:
        # If we have a non-zero fill value, we locate those entries by
        # doing a nan-divide.
        # If S was finite, then length is finite (except for small positions)
        length[small_idx] = np.nan
        Snorm[:] = S / length
        Snorm[np.isnan(Snorm)] = fill_norm
    else:
        # Set small values to zero by doing an inf-divide.
        # This is safe (by IEEE-754) as long as S is finite.
        length[small_idx] = np.inf
        Snorm[:] = S / length

    return Snorm
    
def get_window(window, Nx, *, fftbins=True):
   
    if callable(window):
        return window(Nx)

    elif isinstance(window, (str, tuple)) or np.isscalar(window):
        # TODO: if we add custom window functions in librosa, call them here

        return scipy.signal.get_window(window, Nx, fftbins=fftbins)

    elif isinstance(window, (np.ndarray, list)):
        if len(window) == Nx:
            return np.asarray(window)

        raise ParameterError(
            "Window size mismatch: " "{:d} != {:d}".format(len(window), Nx)
        )
    else:
        raise ParameterError("Invalid window specification: {}".format(window))

    
def __window_ss_fill(x, win_sq, n_frames, hop_length):  # pragma: no cover
    """Helper function for window sum-square calculation."""

    n = len(x)
    n_fft = len(win_sq)
    for i in range(n_frames):
        sample = i * hop_length
        x[sample : min(n, sample + n_fft)] += win_sq[: max(0, min(n_fft, n - sample))]
    
def window_sumsquare(
    *,
    window,
    n_frames,
    hop_length=512,
    win_length=None,
    n_fft=2048,
    dtype=np.float32,
    norm=None,
):
   
    if win_length is None:
        win_length = n_fft

    n = n_fft + hop_length * (n_frames - 1)
    x = np.zeros(n, dtype=dtype)

    # Compute the squared window at the desired length
    win_sq = get_window(window, win_length)
    win_sq = normalize(win_sq, norm=norm) ** 2
    win_sq = pad_center(win_sq, size=n_fft)

    # Fill the envelope
    __window_ss_fill(x, win_sq, n_frames, hop_length)

    return x

    
def istft(
    stft_matrix,
    *,
    hop_length=None,
    win_length=None,
    n_fft=None,
    window="hann",
    center=True,
    dtype=None,
    length=None,
):
    
    if n_fft is None:
        n_fft = 2 * (stft_matrix.shape[-2] - 1)

    # By default, use the entire frame
    if win_length is None:
        win_length = n_fft

    # Set the default hop, if it's not already specified
    if hop_length is None:
        hop_length = int(win_length // 4)

    ifft_window = get_window(window, win_length, fftbins=True)

    # Pad out to match n_fft, and add broadcasting axes
    ifft_window = pad_center(ifft_window, size=n_fft)
    ifft_window = expand_to(ifft_window, ndim=stft_matrix.ndim, axes=-2)

    # For efficiency, trim STFT frames according to signal length if available
    if length:
        if center:
            padded_length = length + int(n_fft)
        else:
            padded_length = length
        n_frames = min(stft_matrix.shape[-1], int(np.ceil(padded_length / hop_length)))
    else:
        n_frames = stft_matrix.shape[-1]

    if dtype is None:
        dtype = dtype_c2r(stft_matrix.dtype)

    shape = list(stft_matrix.shape[:-2])
    expected_signal_len = n_fft + hop_length * (n_frames - 1)
    shape.append(expected_signal_len)
    y = np.zeros(shape, dtype=dtype)

    n_columns = MAX_MEM_BLOCK // (
        np.prod(stft_matrix.shape[:-1]) * stft_matrix.itemsize
    )
    n_columns = max(n_columns, 1)

    from numpy import fft

    frame = 0
    for bl_s in range(0, n_frames, n_columns):
        bl_t = min(bl_s + n_columns, n_frames)

        # invert the block and apply the window function
        ytmp = ifft_window * fft.irfft(stft_matrix[..., bl_s:bl_t], n=n_fft, axis=-2)

        # Overlap-add the istft block starting at the i'th frame
        __overlap_add(y[..., frame * hop_length :], ytmp, hop_length)

        frame += bl_t - bl_s

    # Normalize by sum of squared window
    ifft_window_sum = window_sumsquare(
        window=window,
        n_frames=n_frames,
        win_length=win_length,
        n_fft=n_fft,
        hop_length=hop_length,
        dtype=dtype,
    )

    approx_nonzero_indices = ifft_window_sum > tiny(ifft_window_sum)
    y[..., approx_nonzero_indices] /= ifft_window_sum[approx_nonzero_indices]

    if length is None:
        # If we don't need to control length, just do the usual center trimming
        # to eliminate padded data
        if center:
            y = y[..., int(n_fft // 2) : -int(n_fft // 2)]
    else:
        if center:
            # If we're centering, crop off the first n_fft//2 samples
            # and then trim/pad to the target length.
            # We don't trim the end here, so that if the signal is zero-padded
            # to a longer duration, the decay is smooth by windowing
            start = int(n_fft // 2)
        else:
            # If we're not centering, start at 0 and trim/pad as necessary
            start = 0

        y = fix_length(y[..., start:], size=length)

    return y


def pad_center(data, size, axis=-1, **kwargs):

    kwargs.setdefault('mode', 'constant')

    n = data.shape[axis]

    lpad = int((size - n) // 2)

    lengths = [(0, 0)] * data.ndim
    lengths[axis] = (lpad, int(size - n - lpad))

    if lpad < 0:
        raise ParameterError(('Target size ({:d}) must be '
                              'at least input size ({:d})').format(size, n))

    return np.pad(data, lengths, **kwargs)

def valid_audio(y, mono=True):
    if not isinstance(y, np.ndarray):
        raise ParameterError('data must be of type numpy.ndarray')

    if not np.issubdtype(y.dtype, np.floating):
        raise ParameterError('data must be floating-point')

    if mono and y.ndim != 1:
        raise ParameterError('Invalid shape for monophonic audio: '
                             'ndim={:d}, shape={}'.format(y.ndim, y.shape))

    elif y.ndim > 2 or y.ndim == 0:
        raise ParameterError('Audio must have shape (samples,) or (channels, samples). '
                             'Received shape={}'.format(y.shape))

    if not np.isfinite(y).all():
        raise ParameterError('Audio buffer is not finite everywhere')

    return True
	
def frame(y, frame_length=2048, hop_length=512):

    if not isinstance(y, np.ndarray):
        raise ParameterError('Input must be of type numpy.ndarray, '
                             'given type(y)={}'.format(type(y)))

    if y.ndim != 1:
        raise ParameterError('Input must be one-dimensional, '
                             'given y.ndim={}'.format(y.ndim))

    if len(y) < frame_length:
        raise ParameterError('Buffer is too short (n={:d})'
                             ' for frame_length={:d}'.format(len(y), frame_length))

    if hop_length < 1:
        raise ParameterError('Invalid hop_length: {:d}'.format(hop_length))

    if not y.flags['C_CONTIGUOUS']:
        raise ParameterError('Input buffer must be contiguous.')

    # Compute the number of frames that will fit. The end may get truncated.
    n_frames = 1 + int((len(y) - frame_length) / hop_length)

    # Vertical stride is one sample
    # Horizontal stride is `hop_length` samples
    y_frames = as_strided(y, shape=(frame_length, n_frames),
                          strides=(y.itemsize, hop_length * y.itemsize))
    return y_frames
	
def power_to_db(S, ref=1.0, amin=1e-10, top_db=80.0):
  

    S = np.asarray(S)

    if amin <= 0:
        raise ParameterError('amin must be strictly positive')

    if np.issubdtype(S.dtype, np.complexfloating):
        print('power_to_db was called on complex input so phase '
                      'information will be discarded. To suppress this warning, '
                      'call power_to_db(magphase(D, power=2)[0]) instead.')
        magnitude = np.abs(S)
    else:
        magnitude = S

    if six.callable(ref):
        # User supplied a function to calculate reference power
        ref_value = ref(magnitude)
    else:
        ref_value = np.abs(ref)

    log_spec = 10.0 * np.log10(np.maximum(amin, magnitude))
    log_spec -= 10.0 * np.log10(np.maximum(amin, ref_value))

    if top_db is not None:
        if top_db < 0:
            raise ParameterError('top_db must be non-negative')
        log_spec = np.maximum(log_spec, log_spec.max() - top_db)

    return log_spec	


def amplitude_to_db(S, ref=1.0, amin=1e-5, top_db=80.0):
    S = np.asarray(S)

    if np.issubdtype(S.dtype, np.complexfloating):
        print('amplitude_to_db was called on complex input so phase '
                      'information will be discarded. To suppress this warning, '
                      'call amplitude_to_db(magphase(D)[0]) instead.')

    magnitude = np.abs(S)

    if six.callable(ref):
        # User supplied a function to calculate reference power
        ref_value = ref(magnitude)
    else:
        ref_value = np.abs(ref)

    power = np.square(magnitude, out=magnitude)

    return power_to_db(power, ref=ref_value**2, amin=amin**2,
                       top_db=top_db)
					   
					   
def STFT(y, n_fft=2048, hop_length=None, win_length=None, window='hann',
         center=True, dtype=np.complex64, pad_mode='reflect'):
    # By default, use the entire frame
    if win_length is None:
        win_length = n_fft

    # Set the default hop, if it's not already specified
    if hop_length is None:
        hop_length = int(win_length // 4)

    fft_window = get_window(window, win_length, fftbins=True)

    # Pad the window out to n_fft size
    fft_window = pad_center(fft_window, n_fft)

    # Reshape so that the window can be broadcast
    fft_window = fft_window.reshape((-1, 1))

    # Check audio is valid
    valid_audio(y)

    # Pad the time series so that frames are centered
    if center:
        y = np.pad(y, int(n_fft // 2), mode=pad_mode)

    # Window the time series.
    y_frames = frame(y, frame_length=n_fft, hop_length=hop_length)

    # Pre-allocate the STFT matrix
    stft_matrix = np.empty((int(1 + n_fft // 2), y_frames.shape[1]),
                           dtype=dtype,
                           order='F')

    # how many columns can we fit within MAX_MEM_BLOCK?
    n_columns = int(MAX_MEM_BLOCK / (stft_matrix.shape[0] *
                                          stft_matrix.itemsize))

    for bl_s in range(0, stft_matrix.shape[1], n_columns):
        bl_t = min(bl_s + n_columns, stft_matrix.shape[1])

        # RFFT and Conjugate here to match phase from DPWE code
        stft_matrix[:, bl_s:bl_t] = fft.fft(fft_window *
                                            y_frames[:, bl_s:bl_t],
                                            axis=0)[:stft_matrix.shape[0]]

    return stft_matrix


def get_window(window, Nx, fftbins=True):
    if six.callable(window):
        return window(Nx)

    elif (isinstance(window, (six.string_types, tuple)) or
          np.isscalar(window)):
        # TODO: if we add custom window functions in librosa, call them here

        return scipy.signal.get_window(window, Nx, fftbins=fftbins)

    elif isinstance(window, (np.ndarray, list)):
        if len(window) == Nx:
            return np.asarray(window)

        raise ParameterError('Window size mismatch: '
                             '{:d} != {:d}'.format(len(window), Nx))
    else:
        raise ParameterError('Invalid window specification: {}'.format(window))

def hz_to_mel(frequencies, htk=False):

    frequencies = np.asanyarray(frequencies)

    if htk:
        return 2595.0 * np.log10(1.0 + frequencies / 700.0)

    # Fill in the linear part
    f_min = 0.0
    f_sp = 200.0 / 3

    mels = (frequencies - f_min) / f_sp

    # Fill in the log-scale part

    min_log_hz = 1000.0                         # beginning of log region (Hz)
    min_log_mel = (min_log_hz - f_min) / f_sp   # same (Mels)
    logstep = np.log(6.4) / 27.0                # step size for log region

    if frequencies.ndim:
        # If we have array data, vectorize
        log_t = (frequencies >= min_log_hz)
        mels[log_t] = min_log_mel + np.log(frequencies[log_t]/min_log_hz) / logstep
    elif frequencies >= min_log_hz:
        # If we have scalar data, heck directly
        mels = min_log_mel + np.log(frequencies / min_log_hz) / logstep

    return mels

def mel_to_hz(mels, htk=False):
   
    mels = np.asanyarray(mels)

    if htk:
        return 700.0 * (10.0**(mels / 2595.0) - 1.0)

    # Fill in the linear scale
    f_min = 0.0
    f_sp = 200.0 / 3
    freqs = f_min + f_sp * mels

    # And now the nonlinear scale
    min_log_hz = 1000.0                         # beginning of log region (Hz)
    min_log_mel = (min_log_hz - f_min) / f_sp   # same (Mels)
    logstep = np.log(6.4) / 27.0                # step size for log region

    if mels.ndim:
        # If we have vector data, vectorize
        log_t = (mels >= min_log_mel)
        freqs[log_t] = min_log_hz * np.exp(logstep * (mels[log_t] - min_log_mel))
    elif mels >= min_log_mel:
        # If we have scalar data, check directly
        freqs = min_log_hz * np.exp(logstep * (mels - min_log_mel))

    return freqs


def fft_frequencies(sr=22050, n_fft=2048):


    return np.linspace(0,
                       float(sr) / 2,
                       int(1 + n_fft//2),
                       endpoint=True)

def mel_frequencies(n_mels=128, fmin=0.0, fmax=11025.0, htk=False):

    # 'Center freqs' of mel bands - uniformly spaced between limits
    min_mel = hz_to_mel(fmin, htk=htk)
    max_mel = hz_to_mel(fmax, htk=htk)

    mels = np.linspace(min_mel, max_mel, n_mels)

    return mel_to_hz(mels, htk=htk)

def MEL(sr, n_fft, n_mels=128, fmin=0.0, fmax=None, htk=False,
        norm=1):

    if fmax is None:
        fmax = float(sr) / 2

    if norm is not None and norm != 1 and norm != np.inf:
        raise ParameterError('Unsupported norm: {}'.format(repr(norm)))

    # Initialize the weights
    n_mels = int(n_mels)
    weights = np.zeros((n_mels, int(1 + n_fft // 2)))

    # Center freqs of each FFT bin
    fftfreqs = fft_frequencies(sr=sr, n_fft=n_fft)

    # 'Center freqs' of mel bands - uniformly spaced between limits
    mel_f = mel_frequencies(n_mels + 2, fmin=fmin, fmax=fmax, htk=htk)

    fdiff = np.diff(mel_f)
    ramps = np.subtract.outer(mel_f, fftfreqs)

    for i in range(n_mels):
        # lower and upper slopes for all bins
        lower = -ramps[i] / fdiff[i]
        upper = ramps[i+2] / fdiff[i+1]

        # .. then intersect them with each other and zero
        weights[i] = np.maximum(0, np.minimum(lower, upper))

    if norm == 1:
        # Slaney-style mel is scaled to be approx constant energy per channel
        enorm = 2.0 / (mel_f[2:n_mels+2] - mel_f[:n_mels])
        weights *= enorm[:, np.newaxis]

    # Only check weights if f_mel[0] is positive
    if not np.all((mel_f[:-2] == 0) | (weights.max(axis=1) > 0)):
        # This means we have an empty channel somewhere
        print('Empty filters detected in mel frequency basis. '
                      'Some channels will produce empty responses. '
                      'Try increasing your sampling rate (and fmax) or '
                      'reducing n_mels.')

    return weights

def dct(n_filters, n_input):
    basis = np.empty((n_filters, n_input))
    basis[0, :] = 1.0 / np.sqrt(n_input)

    samples = np.arange(1, 2*n_input, 2) * np.pi / (2.0 * n_input)

    for i in range(1, n_filters):
        basis[i, :] = np.cos(i*samples) * np.sqrt(2.0/n_input)

    return basis