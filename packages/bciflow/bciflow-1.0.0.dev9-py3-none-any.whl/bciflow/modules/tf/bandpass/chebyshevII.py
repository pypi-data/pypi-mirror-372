'''
Description
-----------
This module implements a Chebyshev Type II bandpass filter for EEG data. 
The `chebyshevII` function applies a recursive filter with a steeper roll-off 
and controlled stopband ripple.

Function
------------
'''
import numpy as np
from scipy.signal import cheby2, filtfilt

def chebyshevII(eegdata, low_cut=4, high_cut=40, btype='bandpass', order=4, rs='auto'):
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
    kind_bp : str
        The type of filter ('bandpass', 'lowpass', 'highpass', etc., default is 'bandpass').
    order : int
        The order of the filter (default is 4).
    rs : str
        The minimum attenuation in the stopband (default is 'auto', 
        which sets 40 dB for bandpass and 20 dB for other types).

    Returns
    -------
    output : dict
        The original dictionary with the filtered data stored under the key 'X'.
    '''
    Wn = [low_cut, high_cut]
    
    if rs == 'auto':
        if btype == 'bandpass':
            rs = 40
        else:
            rs = 20

    X = eegdata['X'].copy()
    X = X.reshape((np.prod(X.shape[:-1]), X.shape[-1]))

    X_ = []
    for signal_ in range(X.shape[0]):
        filtered = filtfilt(*cheby2(order, rs, Wn, btype, fs=eegdata['sfreq']), X[signal_])
        X_.append(filtered)

    X_ = np.array(X_)
    X_ = X_.reshape(eegdata['X'].shape)

    eegdata['X'] = X_

    return eegdata