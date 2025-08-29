'''
Description
-----------
This module implements Empirical Mode Decomposition (EMD) for EEG data. 
The `EMD` function decomposes the input signals into Intrinsic Mode 
Functions (IMFs), which are oscillatory components extracted from the data.

Function
------------
'''
import numpy as np
import emd

def EMD(eegdata, n_imfs=5):
    '''
    Parameters
    ----------
    eegdata : dict
        A dictionary containing the EEG data, where the key 'X' holds the raw signal.
    n_imfs : int
        The number of IMFs to extract (default is 5).

    Returns
    -------
    dict
        The same dictionary passed in parameters, but with the transformed data stored under the key 'X'. The shape of the transformed data is (n_trials, n_imfs, n_electrodes, n_samples).


    Raises
    -------
    ValueError 
        If the input data does not have exactly one band (shape[1] != 1).
    
    '''
    X = eegdata['X'].copy()
    # verify if the data has only one band
    if X.shape[1] != 1:
        raise ValueError('The input data must have only one band.')
    X = X.reshape((np.prod(X.shape[:-1]), X.shape[-1]))

    X_ = []

    for signal_ in range(X.shape[0]):
        try:
            imfs_ = emd.sift.sift(X[signal_], max_imfs=None).T
        except:
            imfs_ = np.random.rand(n_imfs, X.shape[-1]) * 1e-6

        if len(imfs_) > n_imfs:
            imfs_[n_imfs-1] = np.sum(imfs_[n_imfs-1:], axis=0)
            imfs_ = imfs_[:n_imfs]
        elif len(imfs_) < n_imfs:
            imfs_ = np.concatenate((imfs_, np.zeros((n_imfs-len(imfs_), X.shape[-1]))), axis=0)
        
        X_.append(imfs_)

    X_ = np.array(X_)
    X_ = X_.reshape(eegdata['X'].shape[0], eegdata['X'].shape[2],n_imfs*eegdata['X'].shape[1], eegdata['X'].shape[3])
    X_ = np.transpose(X_, (0, 2, 1, 3))
    eegdata['X'] = X_

    return eegdata