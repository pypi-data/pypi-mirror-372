import numpy as np
from scipy.io import loadmat
from typing import Optional, Dict, Any, List


def attention(
    subject: int = 1,
    path: str = 'data/attention/',
    labels: List[str] = ['focused', 'unfocused', 'drowsy'],
) -> Dict[str, Any]:
    """
    Description
    -----------
    This function loads EEG data for a specific subject and session from the attention dataset.
    It processes the data to fit the structure of the `eegdata` dictionary, which is used
    for further processing and analysis.

    The dataset can be found at:
     - https://www.kaggle.com/datasets/inancigdem/eeg-data-for-mental-attention-state-detection

    Parameters
    ----------
    subject : int
        index of the subject to retrieve the data from
    path : str
        Path to the .mat file.

    Returns
    -------
    dict
        Dictionary with:
            X: EEG data as [1, 1, channels, samples].
            y: Labels per sample.
            sfreq: Sampling frequency.
            y_dict: Label mapping dictionary.
            events: Event segments dictionary.
            ch_names: Channel names.
            tmin: Start time (0.0).
            data_type: Type of the data ('raw').

    Examples
    --------
    Load EEG data for subject 1, all sessions, and default labels:

    >>> from bciflow.datasets import attention
    >>> eeg_data = attention(subject=1)
    >>> print(eeg_data['X'].shape)  # Shape of the EEG data
    >>> print(eeg_data['y'])  # Labels
    '''
    """

    # Check if the subject input is valid
    if type(subject) != int:
        raise ValueError("subject has to be an int type value")
    if subject > 34 or subject < 1:
        raise ValueError("subject has to be between 1 and 34")
    if type(labels) != list:
        raise ValueError("labels has to be a list type value")
    for i in labels:
        if i not in ['focused', 'unfocused']:
            raise ValueError("labels has to be a sublist of ['focused', 'unfocused']")
    if type(path) != str:
        raise ValueError("path has to be a str type value")
    if path[-1] != '/':
        path += '/'


    mat = loadmat("EEG Data/eeg_record14.mat")
    o = mat['o'][0][0]



    sfreq = o[3][0][0]                  # Frequência de amostragem (128.0)
    labels = o[4].flatten()             # Labels por amostra (308868,)
    timestamps = o[5]                   # shape (308868, 6)
    meta = o[6]                         # shape (308868, 25)

    eeg_continuo = meta[:, 2:16].T      # shape (14, 308868)


    X = np.expand_dims(np.expand_dims(eeg_continuo, axis=0), axis=0) # shape (1, 1, 14, 308868)
    sfreq = int(o[3][0][0])
    y = labels.shape[0]
    n_amostras = labels.shape[0]

    labels = np.zeros(n_amostras, dtype=np.uint8) # até 10 minutos
    focus_end = int(10 * 60 * sfreq) # a partir de 10 minutos 
    unfocus_end = int(20 * 60 * sfreq) # a partir de 20 minutos

    labels[focus_end:unfocus_end] = 1 # de 10 a 20 minutos todos 1
    labels[unfocus_end:] = 2 # de 20 minutos em diante todos 2

    events = {
    "focused": [0,600],
    "unfocused": [600,1200],
    "drowsy": [1200,2100],
    }
    ch_names = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1',
                'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']

    y_dict = {"focused": 0, "unfocused": 1, "drowsy": 2}
    tmin = 0.0

    labels_dict = {0:'focused-hand', 1: 'unfocused-hand',2:"both-drowsy"}
    y = np.array([labels_dict[i] for i in y])
    selected_labels = np.isin(y, labels)
    X, y = X[selected_labels], y[selected_labels]
    y_dict = {labels[i]: i for i in range(len(labels))}
    y = np.array([y_dict[i] for i in y])

    tmin = 0.0

    dataset = {
        'X': X,                     
        'y': y,           
        'sfreq': sfreq,
        'y_dict': y_dict,
        'events': events,
        'ch_names': ch_names,
        'tmin': tmin,
        'data_type': "epochs"
    }
    return dataset
