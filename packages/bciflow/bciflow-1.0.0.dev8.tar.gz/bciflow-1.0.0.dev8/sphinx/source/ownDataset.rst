How to use a custom ``dataset`` with ``bciflow`` library
=========================================================

Introduction
------------

This tutorial explains how to correctly create the ``dataset`` dictionary required by the ``kfold`` function. You can build this dictionary with your own data, as long as it follows the expected structure defined by the library.

Expected Structure of ``dataset``
----------------------------------

The ``dataset`` is a dictionary with the following fields:

- ``X``: EEG array with shape ``(trials, bands, channels, time)``;
- ``y``: vector with class labels (one per trial);
- ``sfreq``: sampling frequency of the EEG signal (in Hz);
- ``y_dict``: dictionary mapping integer labels to class names;
- ``events``: dictionary with event markers per trial;
- ``ch_names``: list of channel names;
- ``tmin``: time offset relative to the event (in seconds).

Example with Comments
----------------------

.. code-block:: python
    :caption: Building the dataset dictionary

    import numpy as np
    from bciflow.modules.core.kfold import kfold
    from bciflow.modules.tf.bandpass.chebyshevII import chebyshevII
    from bciflow.modules.fe.logpower import logpower
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as lda

    # === EEG data shaped as (trials, bands, channels, time) ===
    X = np.array([])  # Your EEG data must follow this format

    # === Label vector (one integer per trial) ===
    y = np.array([])

    # === Sampling frequency (in Hz) ===
    sfreq = float  # Example: 250.0

    # === Dictionary mapping labels to class names ===
    y_dict = {"class": int, ...}  # Example: {0: "left hand", 1: "right hand"}

    # === Dictionary with event timings (in seconds) ===
    events = {"Task": float, ...}  # Example: {"cue": [2.0, 2.5, 3.0, ...]}

    # === List of EEG channel names ===
    ch_names = list  # Example: ['C3', 'Cz', 'C4']

    # === Time offset relative to the event ===
    tmin = float  # Example: 0.5

    # Group all elements into a single dictionary
    dataset = {
        'X': X,
        'y': y,
        'sfreq': sfreq,
        'y_dict': y_dict,
        'events': events,
        'ch_names': ch_names,
        'tmin': tmin
    }

Next Steps
-----------

Once the ``dataset`` dictionary is properly created, you are ready to use it directly in the ``kfold`` pipeline. This dictionary becomes the main input for the evaluation and processing pipeline, allowing you to apply preprocessing, feature extraction, and classification modules in a structured and repeatable way.

For a more complete example of a typical use case---including filtering, feature extraction, and classification with the FBCSP method---we recommend referring to the introductory tutorial provided with the ``bciflow`` library. That tutorial demonstrates how to set up and run a full pipeline from start to finish using sample data and the FBCSP algorithm.
