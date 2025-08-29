# BCI Flow
Bciflow is a Python package focused on Brain-Computer Interface (BCI)-related work. It provides tools for loading pre-established datasets, performing analysis, pre-processing, filtering, feature extraction, and classification, covering the entire process of creating BCI models. Installation 

You can install bciflow directly from PyPI using pip: 

	pip install bciflow 

## Features 
- **Dataset Loading:** Support for popular BCI datasets, such as BCI Competition datasets, OpenBMI, among others. 
- **Pre-processing:** Filtering, artifact removal, normalization, and other data preparation techniques. 
- **Feature Extraction:** Methods for extracting relevant features from EEG signals, such as frequency bands, CSP (Common Spatial Patterns), etc. 
- **Classification:** Implementation of classification algorithms such as SVM, LDA, Neural Networks, among others. 
- **Complete Pipeline:** Facilitates the creation of complete pipelines for processing and analyzing BCI data.

## Loading a Dataset

The datasets must be loaded by the user, and the data path must be provided by the user in the path parameter. For example, to load the CBCIC dataset:

    from bciflow.datasets import cbcic
    # Load CBCIC dataset
    data = cbcic(
        subject=1,  # Subject number
        session_list=None,  # List of sessions to load (default: all sessions)
        labels=['left-hand', 'right-hand'],  # Labels to include
        path='data/cbcic/'  # Path to the dataset files
    )


## Implemented Methods

| Method                                             | Category             | Implemented |
|----------------------------------------------------|----------------------|-------------|
| **Temporal Filtering**                             |                      |             |
| Bandpass Filtering                                 | Temporal Filtering   | Yes |
| Chebyshev II Filter                                | Pre-processing       | Yes |
| Signal Convolution                                 | Pre-processing       | Yes |
| Empirical Mode Decomposition (EMD)                 | Temporal Filtering   | Yes |
| Filter Bank (ChebyshevII)                          | Temporal Filtering   | Yes |
| Filter Bank (Convolution)                          | Temporal Filtering   | Yes |
| Cubic Resampling                                   | Temporal Filtering   | No |
| FFT-based Resampling                               | Temporal Filtering   | No |
| Wavelet                                            | Temporal Filtering   | Yes |
| Short-Time Fourier Transform (STFT)                | Temporal Filtering   | No |
|                                                    |                      |             |
| **Spatial Filtering**                              |                      |             |
| Common Spatial Patterns (CSP)                      | Spatial Filtering    | Yes |
| Euclidean Alignment (EA)                           | Spatial Filtering    | Yes |
|                                                    |                      |             |
| **Feature Extraction**                             |                      |             |
| Average Power Spectral Density (APSD)              | Feature Extraction   | Yes |
| Curve Length                                       | Feature Extraction   | Yes |
| Log Power                                          | Feature Extraction   | Yes |
| Nonlinear Energy                                   | Feature Extraction   | Yes |
| Welch Periodogram                                  | Feature Extraction   | Yes |
| Canonical Correlation Analysis (CCA)               | Feature Extraction   | No |
| Logarithmic PSD (LPSD)                             | Feature Extraction   | No |
|                                                    |                      |             |
| **Feature Selection**                              |                      |             |
| Mutual Information Best Individual Features (MIBIF)| Feature Selection    | Yes |
|                                                    |                      |             |
| **Classification**                                 |                      |             |
| Naive Bayes Parzen Window (NBPW)                   | Classification       | Yes |
|                                                    |                      |             |
| **Data Augmentation**                              |                      |             |
| EMD-based Augmentation (emdaug)                    | Data Augmentation    | No |
| Gaussian Noise (gaussiannoise)                     | Data Augmentation    | No |
| Time-frequency Gaussian Noise (tfgaussiannoise)    | Data Augmentation    | No |
| Time-frequency Recombination (tfrecombination)     | Data Augmentation    | No |



