import numpy as np
import mne
import os
from typing import Dict, Any

def dreams_dataset(
    path="Data/DatabaseREMs/",
    subject=1,
    dataGroups = ["EEG","EOG","EMG", "ECG", "Resp", "Oxímetro", "Outros"],
    dataType = "raw",
) -> Dict[str, Any]:
    """
    Description
    -----------
    This function loads EEG and associated biosignals from the 
    The DREAMS REMs Database.
    It allows loading signals from different channel groups 
    (EEG, EOG, EMG, ECG, respiratory, oximeter, others), and 
    can return either continuous raw signals or windowed epochs.  
    If available, the hypnogram labels (sleep stages) are also loaded.  

    The dataset can be found at:
    - https://zenodo.org/records/2650142

    Parameters
    ----------
    path : str
        Path to the folder containing the DREAMS dataset files 
        (EDF and hypnogram text files).
    subject : int
        Index of the subject to load (e.g., subject=1 loads `excerpt1.edf`).
    dataGroups : list of str
        List of signal groups to include in the dataset. 
        Options include ["EEG","EOG","EMG","ECG","Resp","Oxímetro","Outros"].
    dataType : str
        Type of data representation:
            - "raw" : returns continuous signals concatenated in time.
            - "epochs" : returns segmented windowed trials (default window = 5s).

    Returns
    -------
    dict
        A dictionary containing the following keys:

        - X: EEG data as a numpy array [trials, 1, channels, time] or [1, 1, channels, samples].
        - y: Labels corresponding to the EEG data (expanded per sample if raw, per trial if epochs).
        - sfreq: Sampling frequency of the EEG data.
        - y_dict: Mapping of labels to integers.
        - events: Dictionary describing event markers.
        - ch_names: List of channel names.
        - tmin: Start time of the EEG data.
        - data_type: Type of data returned ("raw" or "epochs").

    Raises
    ------
    FileNotFoundError
        If the EDF file for the given subject is not found.

    Examples
    --------
    Load subject 1 data in epochs format:

    >>> from bciflow.datasets import dreams_dataset
    >>> eeg_data = dreams_dataset(subject=1, dataType="epochs")
    >>> print(eeg_data['X'].shape)  # Shape of the EEG data
    >>> print(eeg_data['y'].shape)  # Labels aligned with epochs

    Load subject 2 raw continuous data with EEG + ECG only:

    >>> eeg_data = dreams_dataset(subject=2, dataGroups=["EEG","ECG"], dataType="raw")
    >>> print(eeg_data['X'].shape)  
    >>> print(len(eeg_data['ch_names']))
    """
    
    CHANNEL_GROUPS = {
        "EEG": ["FP1-A2", "FP2-A1", "CZ-A1", "CZ2-A1", "O1-A2", "O2-A1"],
        "EOG": ["EOG1", "EOG2"],
        "EMG": ["EMG1", "EMG2", "EMG3"],
        "ECG": ["ECG", "PULSE"],
        "Resp": ["VTH", "VAB", "VTOT", "NAF1", "NAF2P-A1", "PR", "PCPAP"],
        "Oxímetro": ["SAO2"],
        "Outros": ["PHONO", "POS"]
    }

    window_size= 5.0
    overlap= 0.0
    if path[-1] != '/':
        path += '/'

    edf_file, hypnogram_file = "", ""
    for filename in os.listdir(path):
        if filename == f"Hypnogram_excerpt{subject}.txt":
            hypnogram_file = path + filename
        if filename == f"excerpt{subject}.edf":
            edf_file = path + filename

    if not os.path.exists(edf_file):
        raise FileNotFoundError(f"EDF file not found: {edf_file}")

    if hypnogram_file and not os.path.exists(hypnogram_file):
        print(f"Hypnogram file not found: {hypnogram_file} (proceeding without labels)")
        hypnogram_file = None

    # Load raw EEG
    raw = mne.io.read_raw_edf(edf_file, preload=True, verbose="ERROR")
    sfreq = raw.info['sfreq']
    ch_names = raw.ch_names

    signals = raw.get_data().T  # (samples, channels)

    # Load hypnogram if available
    if hypnogram_file:
        with open(hypnogram_file, "r") as f:
            lines = f.readlines()
        stages = np.array([int(line.strip()) for line in lines[1:]])
    else:
        stages = None

    # Create trials
    samples_per_window = int(window_size * sfreq)
    step = samples_per_window - int(overlap * sfreq)
    total_samples = signals.shape[0]
    trials = []
    for start in range(0, total_samples - samples_per_window + 1, step):
        end = start + samples_per_window
        window = signals[start:end, :].T  # (channels, samples)
        trials.append(window)

    trials = np.array(trials)  # (num_trials, channels, samples)

    _trials = []
    for dataGroup in dataGroups:
        for group, channels in CHANNEL_GROUPS.items():
            if dataGroup == group:
                idxs = [ch_names.index(ch) for ch in channels if ch in ch_names]
                if len(idxs) > 0:
                    _trials = trials[:, idxs, :]  # (trials, chans, samples)

    _X = _trials[:, np.newaxis, :, :]

    # Map sleep stage codes
    y_dict = {
        "Unknown": 0,
        "Stage 1": 1,
        "Stage 2": 2,
        "Stage 3": 3,
        "REM": 4,
        "Awake": 5
    }
    y = []
    if dataType == "raw":
        X = _X.reshape(1,1,_X.shape[2],_X.shape[0]*_X.shape[3])
        _stages = np.repeat(stages, samples_per_window)
        y = _stages
    elif dataType == "epochs":
        X = _X
        y = stages

    return {
        "X": X,
        "y": y,
        "sfreq": sfreq,
        "y_dict": y_dict,
        "events": None,
        "ch_names": ch_names,
        "tmin": 0.0,
        "data_type": dataType
    }
