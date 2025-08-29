from bciflow.datasets.bciciv2b import bciciv2b
from bciflow.modules.core.util import *

data = bciciv2b(subject=1,path='data/BCICIV2b/')
print("0. Dataset shape atual: ",data["X"].shape)
print("1. Timestamps:", util.timestamp(data))
print("2. Shape after crop:", util.crop(data, 0.1, 0.2, inplace=False)["X"].shape)
print("3.1 Trial 1:", data["X"].shape)
print("3.2 Extracted Trial 1:", util.get_trial(data, 1)["X"].shape)

def invert_time(eeg_trial):
    eeg_trial = eeg_trial.copy()
    eeg_trial["X"] = np.flip(eeg_trial["X"],  -1)
    return eeg_trial

applied = util.apply_to_trials(data, invert_time)
print("4.1 Trial 0 of electrode 0 with reverse time:", applied["X"][0,:,0,:5] )
print("4.2 Real trial 0 of electrode 0 last times:", data["X"][0,:,0,-5:])
concat = util.concatenate([data, data])
print("5. Shape when we concatenate data with itself:", concat["X"].shape)