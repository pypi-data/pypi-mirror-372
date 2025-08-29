Data Files
============================

To use this package, it's necessary to have a EEG dictionary, where the data and 
labels from the trials can be acessed. However, all the dataset functions presented 
in this package need the original data, which we don't have the permission to 
distribute. Any user that wants to use any of the dataset functions must have the 
original data from the dataset.

When the dataset is acquired, just create a `data` folder on root and inside it, a 
folder named after the dataset. Or, if necessary, pass the path of the data in 
the function call

Here's a example how to do it:

.. code-block:: python

    eeg_data = cbcic(subject=1)
    print(eeg_data['X'].shape)  # Shape of the EEG data
    print(eeg_data['y'])  # Labels

    