Creating custom functions or classes for the ``kfold`` pipeline
================================================================

Introduction
------------

In EEG decoding pipelines, it is common to evaluate model performance using cross-validation techniques such as ``kfold``, which is our case. To ensure proper modularity and prevent data leakage across folds, the pipeline is typically divided into two main transformation stages: ``pre-folding`` and ``post-folding``.

- ``Pre-folding`` refers to all operations that are applied to the data *before* the fold split. These transformations are shared across all folds and must be strictly independent of the training/testing process. Common examples include filtering, artifact rejection, or epoch extraction.

- ``Post-folding`` transformations, defined through the ``pos_folding`` dictionary, are applied *within each fold*, only after the data has been split into training and testing sets. This guarantees that feature extraction, normalization, or classifier training is done independently for each fold, which is essential to avoid information leakage and obtain reliable cross-validation results.

The separation between these two stages is crucial. Applying operations like scaling or feature extraction globally before folding would cause the test data to influence the learned transformations—this violates cross-validation assumptions and leads to overly optimistic performance estimates.

This tutorial focuses on creating custom ``pre_folding`` and ``pos_folding`` components—either functions or classes—that can be seamlessly integrated into the ``kfold`` pipeline. For the *bciflow* package, we have a distinction from ``pre_folding`` and ``pos_folding``. Only the ``pos_folding`` can have custom classes, while both can have custom functions. 

Basic Usage Pattern
-------------------

An example usage within the ``kfold`` pipeline looks like this:

.. code-block:: python

    tf = function #because it is only used on pre_folding
    tf2 = function #because it can be used on both
    sf = Class() or function #because it is only used on pos_folding
    fe =  Class() or function
    fs =  Class() or function
    pre_folding = {'tf':(tf,{})}
    pos_folding = {
        'tf2':(tf2, {}),
        'sf': (sf, {}),
        'fe':(fe, {'flattening': True}),
        'fs': (fs,{})
        'clf': (lda(), {})
    }

    results = kfold(
        target=dataset, 
        start_window=dataset['events']['cue'][0] + 0.5, 
        pre_folding=pre_folding, 
        pos_folding=pos_folding
    )

Each key in the ``pre_folding`` and ``pos_folding`` dictionary must map to a tuple ``(object, kwargs)``, where:

- ``object`` is a function or class instance
- ``kwargs`` is a dictionary of keyword arguments passed to its ``transform`` method or function call

Component Naming Conventions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The dictionary keys typically follow standardized abbreviations to identify the type of transformation being applied:

- ``sf``: **Spatial Filter** — e.g., CSP, xDAWN, or ICA. Can be applied in both ``pre_folding`` and ``pos_folding``, depending on whether it requires supervision.
- ``tf``: **Temporal Filter** — e.g., bandpass or notch filters. Usually appears in ``pre_folding``, but can also be applied in ``pos_folding`` if it requires adaptation to training data.
- ``fs``: **Feature Selection** — selects relevant features (e.g., variance threshold, mutual information). Must appear only in ``pos_folding`` to avoid data leakage.
- ``fe``: **Feature Extraction** — transforms the data into a feature space (e.g., mean amplitude, power spectral density). Always performed in ``pos_folding``.
- ``clf``: **Classifier** — the final predictive model (e.g., LDA, SVM). Defined in ``pos_folding``.

Pipeline Structure Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Filters (``sf``, ``tf``) may be safely applied in both ``pre_folding`` and ``pos_folding``, depending on whether the transformation is unsupervised (e.g., FIR filters) or supervised (e.g., CSP). In contrast, operations such as ``fs`` (feature selection) and ``fe`` (feature extraction) must be strictly placed in the ``pos_folding`` stage to ensure that only training data is used for parameter estimation, thereby preserving the validity of the cross-validation protocol.

Basic Requirements
------------------

1. If You Use a Function
~~~~~~~~~~~~~~~~~~~~~~~~

The function must have the following signature:

.. code-block:: python

    def my_function(eegdata: dict, **kwargs):
        ...
        return eegdata_transformed

**Requirements:**

- Inputs: ``eegdata``, and optional keyword arguments
- Output: modified version of ``eegdata``

**Example:**

This function removes the mean of the EEG signal along the time dimension, effectively centering the signal for each trial, band, and electrode.

.. code-block:: python

    import numpy as np

    def removeEEGSignalMean(eegdata):
        X = eegdata['X'].copy() 
        # Compute mean over time axis
        mean = np.mean(X, axis=-1, keepdims=True)  # shape: (trials, bands, electrodes, 1)
        
        # Subtract mean from signal
        X_ = X - mean
        eegdata['X'] = X_ # shape: (trials, bands, electrodes, time)
        return eegdata

**Usage:**

.. code-block:: python

    pre_folding = {}
    pos_folding = {
        'tf': (removeEEGSignalMean, {}),
        ...
        'clf': (lda(), {})
    }

**Or**

.. code-block:: python

    pre_folding = {'tf': (removeEEGSignalMean, {}),}
    pos_folding = {
        ...
        'clf': (lda(), {})
    }

2. If You Use a Class
~~~~~~~~~~~~~~~~~~~~~

Your class must implement the following methods:

.. code-block:: python

    class MyTransformer:
        def fit(self, eegdata:dict, **kwargs):
            ...
            return self

        def transform(self, eegdata:dict, **kwargs):
            ...
            return eegdata_transformed
            
        def fit_transform(self, eegdata:dict, **kwargs):
            ...
            return self.fit(eegdata).transform(eegdata)

**Expected Return Types**

All custom steps must comply with the return format expected by the pipeline:

- The ``fit()`` method of a class should return ``self``.
- The ``transform()`` method of a class and any standalone function must return a ``dict``-like object with the structure of ``eegdata``.

The ``eegdata`` dictionary typically includes a key ``'X'``, which contains the EEG data in a 4D array of shape ``(trials, bands, electrodes, time)`` or its flattened variant if ``flattening=True`` is passed.

**Note:** You must always return the updated ``eegdata`` dictionary *even if you perform operations in-place* to ensure the pipeline remains functional and modular.

**Example:**

This class performs standardization (Z-score) across the EEG time domain, considering the shape ``(trials, bands, electrodes, time)``.

.. code-block:: python

    import numpy as np

    class StandardScalerEEG:

        def __init__(self):
            pass

        def fit(self, eegdata: dict):
            X = eegdata['X']
            
            bands, electrodes = X.shape[1], X.shape[2]
            X_reshaped = X.transpose(1, 2, 0, 3).reshape(bands, electrodes, -1)

            self.mean_ = np.mean(X_reshaped, axis=-1, keepdims=True) #shape (bands, electrodes, 1)
            self.std_ = np.std(X_reshaped, axis=-1, keepdims=True) #shape (bands, electrodes, 1)

            return self

        def transform(self, eegdata: dict):
            X = eegdata['X']
            shape = X.shape  #(trials, bands, electrodes, time)
            X_trans = X.transpose(1, 2, 0, 3)  #(bands, electrodes, trials, time)
            X_scaled = (X_trans - self.mean_[..., None]) / self.std_[..., None] #(bands, electrodes, trials, time)
            X_scaled = X_scaled.transpose(2, 0, 1, 3) # volta para (trials, bands, electrodes, time)
            
            eegdata['X'] = X_scaled
            return eegdata

        def fit_transform(self, eegdata: dict):
            return self.fit(eegdata).transform(eegdata)

**Usage:**

.. code-block:: python

    pre_folding = {}
    pos_folding = {
        'sf': (StandardScalerEEG(), {}),
        ...
        'clf': (lda(), {})
    }

These examples demonstrate how both object-oriented and functional styles can be effectively integrated into the pipeline.
