'''
Description
-----------
This module implements cubic resampling for EEG data. 
The `cubic_resample` function uses cubic splines to resample the input 
signals to a new sampling frequency, providing smooth interpolation between data points.

Function
-----------
'''
import numpy as np
from scipy.interpolate import CubicSpline

def cubic_resample(eegdata, new_sfreq):
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
                cubic_spline = CubicSpline(old_times, X[signal_])
                new_signal = cubic_spline(new_times)
                X_.append(new_signal)

    X_ = np.array(X_)
    X_ = X_.reshape(*eegdata['X'].shape[:-1],eegdata['X'].shape[-1]//divisor )

    eegdata['X'] = X_
    eegdata['sfreq'] = new_sfreq

    return eegdata