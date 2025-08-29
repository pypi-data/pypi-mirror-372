from sklearn.model_selection import StratifiedKFold
import numpy as np
import pandas as pd
import inspect
from ..core.util import util
from typing import Dict, Any, List, Optional

def kfold(target: Dict[str, Any],
          start_window: float or list,
          start_test_window: Optional[float or list] = None,
          pre_folding: Optional[Dict[str, tuple]] = None,
          pos_folding: Dict[str, tuple] = {},
          window_size: float = 1.0,
          source: list = None) -> pd.DataFrame:
    '''
    This method is used to perform a stratified k-fold cross-validation. 
    The method is designed to work with eegdata dictionary.

    Parameters
    ----------
    target : dict
        Input EEG data in the form of a dictionary.
        The dictionary should contain the following keys:
        - 'X': The EEG data as a numpy array.
        - 'y': The labels corresponding to the EEG data.
        - 'sfreq': The sampling frequency of the EEG data.
        - 'y_dict': A dictionary mapping the labels to integers.
        - 'events': A dictionary describing the event markers.
        - 'ch_names': A list of channel names.
        - 'tmin': The start time of the EEG data.        
    start_window : int
        The start time of the window to be used in the crop method of eegdata for the training set.
    start_test_window : int
        The start time of the window to be used in the crop method of eegdata for the test set.
    pre_folding : dict
        A dictionary containing the preprocessing functions to be applied to the data before the cross-validation.
        The keys are the names of the preprocessing functions, and the values are tuples containing the function and its parameters.
    pos_folding : dict
        A dictionary containing the postprocessing functions to be applied to the data before the cross-validation.
        The keys are the names of the postprocessing functions, and the values are the functions.
        The 'clf' key is reserved for the classifier, and its value should be a tuple containing the classifier and its parameters.
    window_size : float 
            The size of the window to be used in the crop method of eegdata.
    source : list
        List of Eeg data from anothers subjects to be used as a source for the Transfer Learning modules
    
    Returns
    -------
    results : pandas.DataFrame
        A pandas dataframe containing the results of the cross-validation. 
        The columns are 'fold', 'tmin', 'true_label', and the labels of the events in the target object.

    Raises
    ------
    ValueError
        If any of the input parameters are invalid

    Example
    -------
    Applying k-fold cross-validation on EEG data:

    >>> from bciflow.modules.core.kfold import kfold
    >>> import numpy as np
    >>> target = {
        'X': np.random.rand(100, 64, 256),
        'y': np.random.randint(0, 2, size=100),
        'sfreq': 256,  # Sampling frequency
        'y_dict': {0: 'class_0', 1: 'class_1'},
        'events': {'event_1': [0, 50], 'event_2': [51, 100]},
        'ch_names': [f'ch_{i}' for i in range(64)],
        'tmin': -0.5
    }
    >>> start_window = 0.0
    >>> start_test_window = 0.5
    >>> results = kfold(target, start_window, start_test_window)
    >>> print(results.head())  # Display the first few rows of the results
    '''
    
    if type(start_window) is float:
        start_window = [start_window]

    if start_test_window is None:
        start_test_window = start_window
    elif type(start_test_window) is float:
        start_test_window = [start_test_window]
    # if not isinstance(start_window, list):
    #     raise ValueError("start_window must be a float or a list of floats")
    # if not isinstance(start_test_window, list):
    #     raise ValueError("start_test_window must be a list of floats")

    if pre_folding is None:
        pre_folding = {}

    target_dict = {}
    for tmin_ in start_test_window:
        target_dict[tmin_] = util.crop(data=target, tmin=tmin_, window_size=window_size, inplace=False)
    
    for tmin_ in start_test_window:
        for name, pre_func in pre_folding.items():

            if inspect.isfunction(pre_func[0]):
                target_dict[tmin_] = util.apply_to_trials(data=target_dict[tmin_], func=pre_func[0], func_param=pre_func[1], inplace=False)
            else:
                target_dict[tmin_] = util.apply_to_trials(data=target_dict[tmin_], func=pre_func[0].transform, func_param=pre_func[1], inplace=False)
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    fold_id = 0
    results = []
    for train_index, test_index in skf.split(target["y"], target["y"]):
        fold_id += 1

        target_train = []
        for tmin_ in start_window:
            target_train.append(util.get_trial(data=target_dict[tmin_], ids=train_index))
        target_train = util.concatenate(target_train)

        target_test = {}
        for tmin_ in start_test_window:
            target_test[tmin_] = util.get_trial(data=target_dict[tmin_], ids=test_index)

        for name, pos_func in pos_folding.items():
            
            if name != 'clf':
                if inspect.isfunction(pos_func[0]):
                    target_train = pos_func[0](target_train, **pos_func[1])
                else:
                    target_train = pos_func[0].fit_transform(target_train, **pos_func[1])

                for tmin_ in start_test_window:
                    if inspect.isfunction(pos_func[0]):
                        target_test[tmin_] = pos_func[0](target_test[tmin_], **pos_func[1])
                    else:
                        target_test[tmin_] = pos_func[0].transform(target_test[tmin_])


        clf, clf_param = pos_folding['clf']
        if not inspect.isfunction(clf):
            clf = clf.fit(target_train['X'], target_train['y'], **clf_param)
                
        for tmin_ in start_test_window:
            try:
                y_pred = clf.predict_proba(target_test[tmin_]['X'])
            except:
                y_pred = np.zeros((len(target_test[tmin_]['y']), len(target['y_dict'])))
            y_pred = np.round(y_pred, 4)
            for trial_ in range(len(y_pred)):
                results.append([fold_id, tmin_, util.find_key_with_value(target['y_dict'], target_test[tmin_]['y'][trial_]), *y_pred[trial_]])

    results = np.array(results)
    results = pd.DataFrame(results, columns=['fold', 'tmin', 'true_label', *target['y_dict'].keys()])

    return results