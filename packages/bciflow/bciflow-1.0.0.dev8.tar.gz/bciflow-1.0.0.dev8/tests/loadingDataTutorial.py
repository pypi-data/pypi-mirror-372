
from bciflow.datasets.cbcic import cbcic    

dataset = cbcic(subject=1,path='data/cbcic/')

print("EEG signals shape:", dataset["X"].shape)
print("Labels:", dataset["y"])
print("Class dictionary:", dataset["y_dict"])
print("Events:", dataset["events"])
print("Channel names:", dataset["ch_names"])
print("Sampling frequency (Hz):", dataset["sfreq"])
print("Start time (s):", dataset["tmin"])

