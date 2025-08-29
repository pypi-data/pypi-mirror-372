'''
Description
-----------
This module implements the Curve Length feature extractor, which measures the cumulative 
amplitude changes in EEG signals over time. This feature is useful for capturing the 
complexity and variability of brain activity, making it suitable for tasks like motor 
imagery classification.

The Curve Length is calculated as the sum of the absolute differences between consecutive 
samples in the signal.

Class
------------
'''
import numpy as np

class curvelength():
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
        This method does nothing, as the Curve Length feature extractor does not require training.
        
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

    def transform(self, eegdata) -> dict:
        ''' 
        This method computes the Curve Length for each trial, band, and channel in the input data. 
        The result is stored in the dictionary under the key 'X'.
        
        Parameters
        ----------
        eegdata : dict
            The input data.
        
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
        trials_, bands_, channels_, times_ = X.shape

        for trial_ in range(trials_):
            output.append([])
            for band_ in range(bands_):
                output[trial_].append([]) 
                for channel_ in range(channels_):
                    diff = X[trial_, band_, channel_, 1:] - X[trial_, band_, channel_, :-1]
                    output[trial_][band_].append(np.sum(np.abs(diff)))

        output = np.array(output)
        
        if self.flating:
            output = output.reshape(output.shape[0], -1)

        if not many_trials:
            output = output[0]
        eegdata['X'] = output
        return eegdata
    
    def fit_transform(self, eegdata) -> dict:
        '''
        This method combines fitting and transforming into a single step. It returns a 
        dictionary with the transformed data.
        
        Parameters
        ----------
        eegdata : dict
            The input data.
          
        Returns
        -------
        output : dict
            The transformed data.
        '''
        return self.fit(eegdata).transform(eegdata)

