Loading and Exploring CBCIC dataset using bciflow
================================================

The bciflow library provides convenient tools for working with EEG datasets 
for Brain-Computer Interface (BCI) research. In this tutorial, we will focus 
on loading and exploring the CBCIC dataset using bciflow.

Objectives of this Tutorial
---------------------------

- Learn how to load EEG data from CBCIC dataset using bciflow
- Understand the structure of the dataset
- Print and interpret key dataset components such as EEG signals, labels, and metadata

1. Installation
-----------------

| First, make sure bciflow is installed in your Python environment:

.. code-block:: bash

   pip install bciflow

.. note::
   Ensure you are using Python 3.7 or higher.

2. Loading the Dataset
-----------------------

| We'll use the CBCIC dataset for this tutorial. This is the dataset for the competition "Clinical Brain Computer Interfaces Challenge" to be held at WCCI 2020 at Glasgow.  The dataset contains data from 10 hemiparetic stroke patients who are impaired  either by left or right hand finger mobility.
| Download it from `GitHub Clinical Brain Computer Interfaces Challenge`_.
| Make sure the dataset files are saved in a known folder.
| Now, let's load the data for subject 1:

.. _GitHub Clinical Brain Computer Interfaces Challenge: https://github.com/5anirban9/Clinical-Brain-Computer-Interfaces-Challenge-WCCI-2020-Glasgow

.. code-block:: python

   from bciflow.datasets.CBCIC import cbcic
   
   dataset = cbcic(subject=1, path='data/cbcic/')

.. note::
    This command loads the dataset for subject 1 and stores it in a dictionary called dataset.
    
    Ensure the dataset is available at ``data/cbcic/`` or adjust the path accordingly.

3. Exploring the Dataset Contents
----------------------------------

Let's explore what's inside this dataset. We will print different keys of the
dictionary to understand the data structure.

3.1 EEG Signals: dataset["X"]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   print(dataset["X"])

This prints the EEG signals organized as a 4D array:

* trials: how many repetitions (epochs) of the task were recorded
* frequency_bands: for each trial, the signals are filtered in different frequency bands (if applicable)
* channels: each electrode in the EEG cap used
* time_samples: the EEG signal over time (in samples)

Example shape: ``(120, 1, 12, 4096)`` → 120 trials, 1 frequency band, 12 electrodes, 4096 time samples.
If the frequency is 512Hz, it means that there are 4096 samples in 8 seconds

3.2 Labels per Trial: dataset["y"]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   print(dataset["y"])

| This shows a list of integers representing the class (or task) performed in each trial.
| Example: ``[0, 0, 0, ..., 1, 1, 1]``
| Each number corresponds to a mental task (like left hand, right hand, etc.)

3.3 Class Meaning: dataset["y_dict"]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   print(dataset["y_dict"])

| This prints a dictionary mapping class numbers to their meaning
| Output example: ``{'left-hand': 0, 'right-hand': 1}``
| This tells us what class 0 and 1 mean in dataset["y"].

3.4 Events: dataset["events"]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   print(dataset["events"])

| This shows a dictionary containing event timestamps~:

.. code-block:: python

   {'get_start': [0, 3],
    'beep_sound': [2],
    'cue': [3, 8],
    'task_exec': [3, 8]}

This tells us when each event happened (in seconds) during data collection.
Useful to segment the signals around specific events

3.5 Channel Names: dataset["ch_names"]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   print(dataset["ch_names"])

| This prints a list of EEG channel (electrode) names, e.g.
| Example: ``['F3', 'FC3', 'C3', 'CP3', 'P3', 'FCz', 'CPz', 'P4', 'FC4', 'C4', 'CP4', 'P4']``
| Each name represents a physical location on the EEG cap.

3.6 Sampling Frequency: dataset["sfreq"]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   print(dataset["sfreq"])

Returns the sampling frequency in Hz (e.g., ``512.0``). This tells us how many samples per second were recorded.

3.7 Start Time: dataset["tmin"]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   print(dataset["tmin"])

| Shows the starting time in seconds relative to event markers (e.g., ``0.0``). 
| If it was -1 it would indicate that data starts 1 second before the event (useful for extracting pre-event baselines).

4. Dataset Structure Summary
------------------------

.. list-table:: Dataset Structure
   :header-rows: 1
   :widths: 20 50 30

   * - **Key**
     - **Description**
     - **Example**
   * - ``X``
     - EEG data (trials × bands × channels × time)
     - shape (120, 1, 12, 4096)
   * - ``y``
     - Labels for each trial
     - [0, 0, 0, ...]
   * - ``y_dict``
     - Class mapping
     - {'left-hand': 0, 'right-hand': 1}
   * - ``events``
     - Event timestamps
     - {'get_start': [...]}
   * - ``ch_names``
     - Channel names
     - ['F3', 'FC3', 'C3', ...]
   * - ``sfreq``
     - Sampling frequency (Hz)
     - 512.0
   * - ``tmin``
     - Start time (seconds)
     - 0.0

5. Complete Example Code
---------------------

.. code-block:: python

   from bciflow.datasets.CBCIC import cbcic
   
   dataset = cbcic(subject=1, path='data/cbcic/')
   
   print("EEG signals shape:", dataset["X"].shape)
   print("Labels:", dataset["y"])
   print("Class dictionary:", dataset["y_dict"])
   print("Events:", dataset["events"])
   print("Channel names:", dataset["ch_names"])
   print("Sampling frequency (Hz):", dataset["sfreq"])
   print("Start time (s):", dataset["tmin"])