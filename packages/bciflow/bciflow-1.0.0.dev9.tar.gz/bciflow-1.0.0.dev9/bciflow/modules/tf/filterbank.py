'''
Description
-----------
This module implements a filter bank for EEG data. The `filterbank` 
function applies multiple bandpass filters to the input signal, 
allowing for the extraction of frequency-specific features.

Function
------------
'''
import numpy as np
from bciflow.modules.tf.bandpass.convolution import bandpass_conv
from bciflow.modules.tf.bandpass.chebyshevII import chebyshevII

def filterbank(eegdata, low_cut=[4,8,12,16,20,24,28,32,36], high_cut=[8,12,16,20,24,28,32,36,40], kind_bp='conv', **kwargs):
    '''
    Parameters
    ----------
    eegdata : dict
        A dictionary containing the EEG data, where the key 'X' holds the raw signal.
    low_cut : int or list
        A list of lower cutoff frequencies for each bandpass filter.
    high_cut : int or list
        A list of upper cutoff frequencies for each bandpass filter.
    kind_bp : str
        The type of bandpass filter to use. Options are 'conv' (convolution-based) 
        and 'chebyshevII' (Chebyshev Type II filter)
    kwargs : dict
        Additional arguments to be passed to the filter function.

    Returns
    -------
    output : dict
        The original dictionary with the filtered data stored under the key 'X'.
    '''
    X = eegdata['X'].copy()
    # verify if the data has only one band
    if X.shape[1] != 1:
        raise ValueError('The input data must have only one band.')
    # verify if the low_cut and high_cut have the same length
    if len(low_cut) != len(high_cut):
        raise ValueError('The low_cut and high_cut must have the same length.')
   
    X_ = []
    for trial_ in range(X.shape[0]):
        X_.append([])
        for i in range(len(low_cut)):
            eegdata_ = eegdata.copy()
            eegdata_['X'] = np.array([X[trial_]])
            if kind_bp == 'conv':
                X__ = bandpass_conv(eegdata_, 
                                    low_cut=low_cut[i], 
                                    high_cut=high_cut[i],
                                    kind='same',
                                    **kwargs)['X'][0][0]
                X_[-1].append(X__)
            elif kind_bp == 'chebyshevII':
                X__ = chebyshevII(eegdata_,
                                    low_cut=low_cut[i], 
                                    high_cut=high_cut[i],
                                    **kwargs)['X'][0][0]
                X_[-1].append(X__)

    X_ = np.array(X_)
    
    eegdata['X'] = X_

    return eegdata