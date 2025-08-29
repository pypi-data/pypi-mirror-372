'''
Description
-----------
This module implements FFT-based resampling for EEG data. 
The `fft_resample` function uses the Fast Fourier Transform (FFT) to 
resample the input signals to a new sampling frequency, maintaining 
the spectral properties of the signal.

Function
------------
'''
import numpy as np
from scipy.signal import resample

def fft_resample(eegdata, new_sfreq):
    '''
    Parameters
    ----------
    eegdata : dict
        A dictionary containing the EEG data, where the key 'X' 
        holds the raw signal and 'sfreq' holds the original sampling frequency.
    new_sfreq : float
        The new sampling frequency to which the data will be resampled.

    Returns
    -------
    dict
        The same dictionary passed in parameters, but with the resampled data stored under the key 'X' and the new sampling frequency under the key 'sfreq'.
    '''
    X = eegdata['X'].copy()
    X = X.reshape((np.prod(X.shape[:-1]), X.shape[-1]))
    sfreq = eegdata['sfreq']
    divisor = sfreq//new_sfreq
    duration = X.shape[-1]/sfreq
    old_times = np.arange(0, duration, 1./sfreq)
    new_times = np.arange(0, duration, 1./new_sfreq)

    X_ = []
    for signal_ in range(X.shape[0]):
        new_signal = resample(X[signal_], int(new_times.shape[0]))
        X_.append(new_signal)

    X_ = np.array(X_)
    X_ = X_.reshape(*eegdata['X'].shape[:-1],eegdata['X'].shape[-1]//divisor )

    eegdata['X'] = X_
    eegdata['sfreq'] = new_sfreq

    return eegdata