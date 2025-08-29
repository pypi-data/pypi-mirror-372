'''
Description
-----------
This module implements the Euclidean Alignment (EA) method, a spatial filtering technique 
used to align EEG data from different subjects or sessions to a common reference. 
This reduces inter-subject variability and improves the generalization of BCI models.

The EA method aligns EEG data by transforming it such that the reference matrix becomes 
an identity matrix. This is particularly useful for cross-subject or cross-session 
BCI applications.

Class
------------
'''
from scipy.linalg import fractional_matrix_power
import numpy as np

class ea:
    '''
    Attributes
    ----------
    target_transformation : list-like, size (n_bands)
        List containing the reference matrix for each band of the target subject
    '''
    def __init__(self):   
        self.target_transformation = None
        self.source_transformation = []

    def calc_r(self, data):
        ''' 
        Computes the reference matrix for each frequency band.
        
        Parameters
        ----------
        data : array-like, shape (n_trials, n_bands, n_electodes, n_times)
            The input data from a subject.
        
        returns
        -------
        list_r : list-like, size (n_bands), containing array-like, shape (n_electodes, n_electodes)
            The list of reference matrix from the data.
            
        '''
        list_r = []
        for band in range(data.shape[1]):
            r = np.zeros((data.shape[2], data.shape[2]))
            for trial in range(data.shape[0]):
                product = np.dot(data[trial][band], data[trial][band].T)
                r += product
            r = r / data.shape[0]
            list_r.append(r)
        return np.array(list_r)
    
    def full_r(self, data):
        ''' 
        This method call calc_r, and then raises all matrices to the power of -1/2,
        to transform the input data
        
        Parameters
        ----------
        data : array-like, shape (n_trials, n_bands, n_electodes, n_times)
            The input data from a subject.
            
        Returns
        -------
        list_r_inv : list-like, size (n_bands), containing array-like, shape (n_electodes, n_electodes)
            The list of reference matrix to the power of -1/2 from the data.
            
        '''
        list_r = self.calc_r(data)
        list_r_inv = [fractional_matrix_power(r, -0.5) for r in list_r]
        return np.array(list_r_inv)

    def verify_r(self, matrix, epsilon=1e-10):
        '''
        To check whether the Euclidean alignment was implemented correctly, 
        it is necessary to check whether the data reference matrices after 
        the transformation are equal to the identity matrix. Due to computational errors, 
        all values less than epsilon are considered as 0
        
        Parameters
        ----------
        matrix : array-like, shape (n_electodes, n_electodes)
            A reference matrix.
        epsilon : float
            Number used as parameter to determine whether the matrix and identity
            
        Returns
        -------
        test : bool
            Validation of the matrix being identity or not
        
        '''
        if not isinstance(matrix, np.ndarray) or matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError("A entrada deve ser uma matriz quadrada (2D).")
        if not np.allclose(np.diag(matrix), 1, atol=epsilon):
            return False
        return np.all(np.abs(matrix - np.diag(np.diag(matrix))) < epsilon)
    
    def fit(self, eegdata, source):
        ''' 
        Fits the EA method to the input data, calculating the transformation matrices.
        
        Parameters
        ----------
        eegdata : dict
            The input data.
        
        returns
        -------
        self
            
        '''
        data = eegdata['X'].copy()
        self.target_transformation = self.full_r(data)
        if source is not None:
            for i in range(len(source)):
                data = source[i]['X'].copy()
                self.source_transformation.append(self.full_r(data))
        return self

    def transform(self, eegdata, source = None):
        ''' 
        This method aligns the target subject's data by multiplying it
        by the reference matrix for each band.
        
        Parameters
        ----------
        eegdata : dict
            The input data.
            
        returns
        -------
        output : dict
            The transformed data. 
        '''
        X = eegdata['X'].copy()
        for band in range(X.shape[1]):
            for trial in range(X.shape[0]):
                X[trial][band] = np.dot(self.target_transformation[band], X[trial][band])
        eegdata['X'] = X

        if source is not None:
            for i in range(len(source)):
                X = source[i]['X'].copy()
                for band in range(X.shape[1]):
                    for trial in range(X.shape[0]):
                        X[trial][band] = np.dot(self.source_transformation[i][band], X[trial][band])
                source[i]['X'] = X
            
            combined = eegdata.copy()
            combined['X'] = np.concatenate([s['X'] for s in source], axis=0)
            combined['y'] = np.concatenate([s['y'] for s in source], axis=0)
            eegdata = combined
        return eegdata

    def fit_transform(self, eegdata, source):
        ''' 
        Combines fitting and transforming into a single step.

        Parameters
        ----------
        eegdata : dict
            The input data.
        
        returns
        -------
        output : dict
            The transformed data.
            
        '''
        return self.fit(eegdata, source).transform(eegdata, source)