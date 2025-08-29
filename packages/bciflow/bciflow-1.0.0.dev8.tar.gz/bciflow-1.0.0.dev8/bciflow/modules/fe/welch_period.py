'''
Description
-----------
This module implements the Welch Periodogram feature extractor, which computes the power 
spectral density (PSD) of EEG signals using Welch's method. This feature is commonly used 
in BCI applications to analyze the frequency content of brain activity.

Welch's method divides the signal into overlapping segments, computes the periodogram for 
each segment, and averages the results to reduce noise.

Class
------------
'''
import numpy as np
from scipy.signal import welch

class welch_period():
    '''
    Attributes
    ----------
    flating : bool
        If True, the output data is returned in a flattened format (default is False).
    '''
    def __init__(self, flating: bool = False):
        ''' Initializes the class.
        
        Parameters
        ----------
        flating : bool, optional
            If True, the output data is returned in a flattened format (default is False).
        
        Returns
        -------
        None
        '''
        if type(flating) != bool:
            raise ValueError ("Has to be a boolean type value")
        else:
            self.flating = flating

    def fit(self, eegdata):
        '''
        This method does nothing, as the Welch Periodogram feature extractor does not require training.
        
        Parameters
        ----------
        eegdata : dict
            The input data.
            
        Returns
        -------
        self
        '''
        if type(eegdata) != dict:
            raise ValueError ("Has to be a dict type")         
        return self

    def transform(self, eegdata, sfreq: int) -> dict:
        '''
        This method computes the power spectral density (PSD) using Welch's method for each 
        trial, band, and channel in the input data. The result is stored in the dictionary 
        under the key 'X'.
        
        Parameters
        ----------
        eegdata : dict
            The input data.
        sfreq : int
            The sampling frequency of the EEG data.
        
        Returns
        -------
        output : dict
            The transformed data.
        '''
        if type(eegdata) != dict:
            raise ValueError ("Has to be a dict type")                
        X = eegdata['X'].copy()
            
        many_trials = len(X.shape) == 4
        if not many_trials:
            X = X[np.newaxis, :, :, :]

        output = []
        trials_, bands_, channels_, _ = X.shape

        for trial_ in range(trials_):
            output.append([])
            for band_ in range(bands_):
                output[trial_].append([])
                for channel_ in range(channels_):
                    if X[trial_, band_, channel_, :].std() == 0:
                        output[trial_][band_].append(0)
                    else:
                        output[trial_][band_].append(welch(X[trial_, band_, channel_, :], sfreq))    

        output = np.array(output)
        
        if self.flating:
            output = output.reshape(output.shape[0], -1)

        if not many_trials:
            output = output[0]

        eegdata['X'] = output
        return eegdata
    
    def fit_transform(self, eegdata, sfreq: int) -> dict:
        '''
        This method combines fitting and transforming into a single step. It returns a 
        dictionary with the transformed data.
        
        Parameters
        ----------
        eegdata : dict
            The input data.
        sfreq : int
            The sampling frequency of the EEG data.
            
        Returns
        -------
        output : dict
            The transformed data.
        '''
        return self.fit(eegdata).transform(eegdata, sfreq)
