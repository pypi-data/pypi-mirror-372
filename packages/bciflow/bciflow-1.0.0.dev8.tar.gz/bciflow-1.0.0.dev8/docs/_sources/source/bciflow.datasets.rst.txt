.. _datasets:

========
Datasets
========

Datasets in the context of Brain-Computer Interfaces (BCI) are collections of recorded
brain signals, often accompanied by metadata such as event markers, channel information,
and subject details. These datasets are essential for developing and 
testing algorithms that interpret brain activity, enabling applications like 
neurofeedback, prosthetics control, and communication systems for individuals 
with disabilities.

EEG Dictionary
--------------------------

All following functions returns a dictionary that represents the eeg signals and some useful information about the dataset itself.
The dictionary have the following keys:
   - X: EEG data as a numpy array. The data have the following shape: (n_trials,n_bands, n_eletrode, n_times)
   - y: Labels corresponding to the EEG data.
   - sfreq: Sampling frequency of the EEG data.
   - y_dict: Mapping of labels to integers.
   - events: Dictionary describing event markers.
   - ch_names: List of channel names.
   - tmin: Start time of the EEG data.
   - data_type: Explains how the data is placed inside the dictionary. Type 'epochs' means labels per trial and 'raw' means labels per time.

.. toctree::
   :maxdepth: 1
   :caption: List of datasets
   
   bciflow.datasets.attention
   bciflow.datasets.bciciv2a
   bciflow.datasets.bciciv2b
   bciflow.datasets.cbcic
   bciflow.datasets.dreams
   bciflow.datasets.mengu
   
