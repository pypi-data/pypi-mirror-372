import numpy as np
import pandas as pd
import scipy
import mne
from typing import List, Optional, Dict, Any

def bciciv2a(subject: int=1, 
             session_list: Optional[List[str]] = None,
             labels: List[str] = ['left-hand','right-hand',"both-feet","tongue"],
             path: str = 'data/BCICIV2a/') -> Dict[str, Any]:
    """
    Description
    -----------
        
    This function loads EEG data for a specific subject and session from the bciciv2b dataset.
    It processes the data to fit the structure of the `eegdata` dictionary, which is used
    for further processing and analysis.

    The dataset can be found at:
     - https://www.bbci.de/competition/iv/#download
     - https://www.bbci.de/competition/iv/results/index.html#labels
    
    Parameters
    ----------
        subject : int
            index of the subject to retrieve the data from
        session_list : list, optional
            list of session codes
        labels : dict
            dictionary mapping event names to event codes
        path :
            path to the directory tha contains the datasets files.

    Returns
    -------
    dict
        A dictionary containing the following keys:

        - X: EEG data as a numpy array [trials, 1, channels, time].
        - y: Labels corresponding to the EEG data.
        - sfreq: Sampling frequency of the EEG data.
        - y_dict: Mapping of labels to integers.
        - events: Dictionary describing event markers.
        - ch_names: List of channel names.
        - tmin: Start time of the EEG data.
        - data_type: Type of the data ('epochs').

    Examples
    --------
    Load EEG data for subject 1, all sessions, and default labels:

    >>> from bciflow.datasets import bciciv2a
    >>> eeg_data = bciciv2a(subject=1)
    >>> print(eeg_data['X'].shape)  # Shape of the EEG data
    >>> print(eeg_data['y'])  # Labels
    '''
    """

    if type(subject) != int:
        raise ValueError("Has to be a int type value")
    if subject > 9 or subject < 1:
        raise ValueError("Has to be an existing subject")
    if type(labels) != list:
        raise ValueError("labels has to be a list type value")
    for i in labels:
        if i not in ['left-hand','right-hand','both-feet','tongue']:
            raise ValueError("labels has to be a sublist of ['left-hand','right-hand','both-feet','tongue'],")
    if type(session_list) != list and session_list != None:
        raise ValueError("Has to be an List or None type")
    if path[-1] != '/':
        path += '/'
        
    sfreq = 250.
    events = {'get_start': [0, 2],
                'beep_sound': [0],
                'cue': [2, 3.25],
                'task_exec': [3, 6],
                'break': [6, 7.5]}
    ch_names = ['Fz', 'FC3', 'FC1', 'FCz', 'FC2', 'FC4', 'C5', 'C3',
                'C1', 'Cz', 'C2', 'C4', 'C6', 'CP3', 'CP1', 'CPz',
                'CP2', 'CP4', 'P1', 'Pz', 'P2', 'POz']
    ch_names = np.array(ch_names)
    tmin = 0.

    if session_list is None:
        session_list = ['T', 'E']

    rawData, rawLabels = [], []

    for sec in session_list:
        raw=mne.io.read_raw_gdf(path+'/A%02d%s.gdf'%(subject, sec), preload=True, verbose='ERROR')
        raw_data = raw.get_data()[:22]
        annotations = raw.annotations.to_data_frame()
        first_timestamp = pd.to_datetime(annotations['onset'].iloc[0])
        annotations['onset'] = (pd.to_datetime(annotations['onset']) - first_timestamp).dt.total_seconds()
        annotations['description'] = annotations['description'].astype(int)
        new_trial_time = np.array(annotations[annotations['description']==768]['onset'])

        times_ = np.array(raw.times)
        rawData_ = []
        for trial_ in new_trial_time:
            idx_ = np.where(times_ == trial_)[0][0]
            rawData_.append(raw_data[:, idx_:idx_+1875])
        rawData_ = np.array(rawData_)
        rawLabels_ = np.array(scipy.io.loadmat(path+'/A%02d%s.mat'%(subject, sec))['classlabel']).reshape(-1)

        rawData.append(rawData_)
        rawLabels.append(rawLabels_)



    X, y = np.concatenate(rawData), np.concatenate(rawLabels)
    X = np.reshape(X, (X.shape[0], 1, X.shape[1], X.shape[2]))
    labels_dict = {1: 'left-hand', 2: 'right-hand',3:"both-feet",4:"tongue"}
    y = np.array([labels_dict[i] for i in y])
    selected_labels = np.isin(y, labels)
    X, y = X[selected_labels], y[selected_labels]
    y_dict = {labels[i]: i for i in range(len(labels))}
    y = np.array([y_dict[i] for i in y])

    return {'X': X, 
            'y': y, 
            'sfreq': sfreq, 
            'y_dict': y_dict,
            'events': events, 
            'ch_names': ch_names,
            'tmin': tmin,
            'data_type': "epochs"}
