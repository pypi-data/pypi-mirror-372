'''
Description
-----------
This module implements a convolution-based bandpass filter for EEG data. 
The `bandpass_conv` function uses a kernel derived from windowed sinc 
functions to perform the filtering.

Function
------------
'''
import numpy as np

def bandpass_conv(eegdata, low_cut=4, high_cut=40, transition=None, window_type='hamming', kind='same'):
    '''
    Parameters
    ----------
    eegdata : dict
        A dictionary containing the EEG data, where the key 'X' holds the 
        raw signal and 'sfreq' holds the sampling frequency.
    low_cut : int
        The lower cutoff frequency of the bandpass filter (default is 4 Hz).
    high_cut : int
        The upper cutoff frequency of the bandpass filter (default is 40 Hz).
    transition : int or float
        The transition bandwidth for the filter (default is half the passband width).
    window_type : str
        The type of window used for the sinc function ('hamming' or 'blackman', default is 'hamming').
    kind : str
        The convolution mode ('same' or 'valid', default is 'same').

    Returns
    -------
    output : dict
        The original dictionary with the filtered data stored under the key 'X'.
    '''
    X = eegdata['X'].copy()
    sfreq = eegdata['sfreq']
    X = X.reshape((np.prod(X.shape[:-1]), X.shape[-1]))

    if transition is None:
        transition = (high_cut - low_cut) / 2
    if isinstance(transition, int):
        transition = float(transition)
    if isinstance(transition, float):
        transition = [transition, transition]

    NL = int(4 * sfreq / transition[0])
    NH = int(4 * sfreq / transition[1])


    hlpf = np.sinc(2 * high_cut / sfreq * (np.arange(NH) - (NH - 1) / 2))
    if window_type=='hamming':
        hlpf *= np.hamming(NH)
    elif window_type=='blackman':
        hlpf *= np.blackman(NH)
    hlpf /= np.sum(hlpf)

    hhpf = np.sinc(2 * low_cut / sfreq * (np.arange(NL) - (NL - 1) / 2))
    if window_type=='hamming':
        hhpf *= np.hamming(NL)
    elif window_type=='blackman':
        hhpf *= np.blackman(NL)
    hhpf = -hhpf
    hhpf[(NL - 1) // 2] += 1

    kernel = np.convolve(hlpf, hhpf)
    if len(kernel) > X.shape[-1] and kind == 'same':
        kind = 'valid'

    X_ = []
    for signal_ in range(X.shape[0]):
        filtered = np.convolve(X[signal_], kernel, mode=kind)
        X_.append(filtered)

    X_ = np.array(X_)
    X_ = X_.reshape(eegdata['X'].shape)
    eegdata['X'] = X_
    return eegdata