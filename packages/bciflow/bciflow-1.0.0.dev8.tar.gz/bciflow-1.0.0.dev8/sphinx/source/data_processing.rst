Introduction to Data Processing using bciflow
============================================

The bciflow library is designed for developing Brain-Computer Interface (BCI) systems in Python. 
It provides modular tools for data loading, preprocessing, feature extraction, feature selection, 
and classification of EEG signals.

In this tutorial, you'll learn how to use bciflow to build a complete EEG analysis pipeline, 
applying a well-known BCI algorithm named FBCSP that uses techniques such as filterbank, CSP, logpower, MIBIF, and LDA.

Objectives of this Tutorial
---------------------------

* Introduce the main functionalities of bciflow
* Demonstrate how to load the CBCIC dataset
* Apply correctly the pre-processing and post-processing parts of the pipeline
* Ensure the correct execution of the created pipeline
* Visualize the accuracy of the results

Prerequisites
-------------

* Basic Python knowledge
* Familiarity with EEG and BCI concepts is helpful, but not required

1. Installation
----------------

Install bciflow using pip:

.. code-block:: bash

   pip install bciflow

.. note::
   Ensure you are using Python 3.7 or higher.

2. Loading Data
----------------

We are using the CBCIC dataset (Clinical Brain-Computer Interface Challenge). Then load the data:

.. code-block:: python

   from bciflow.datasets.CBCIC import cbcic
   
   dataset = cbcic(subject=1, path='data/cbcic/')

.. note::
   Ensure the dataset is available at ``data/cbcic/`` or adjust the path accordingly.

3. Preprocessing: Applying a Filterbank
----------------------------------------

To replicate the FBCSP algorithm, first start processing the data by using a
filterbank to apply multiple bandpass filters and capture patterns in different
frequency bands:

.. code-block:: python

   from bciflow.modules.tf.filterbank import filterbank
   
   pre_folding = {'tf': (filterbank, {'kind_bp': 'chebyshevII'})}

4. Building the Post-processing Pipeline
------------------------------------------

After that, we can go to the next stage by adding, in order, the stages of the algorithm:

1. **sf**: :ref:`Common Spatial Patterns (CSP) <csp>` - maximizes discriminative variance
2. **fe**: :ref:`logpower <logpower>` - extracts logarithmic power of filtered signals
3. **fs**: :ref:`MIBIF <mibif>` - selects 8 best features based on mutual information
4. **clf**: LDA classifier - classifies data

.. code-block:: python

   from bciflow.modules.sf.csp import csp
   from bciflow.modules.fe.logpower import logpower
   from bciflow.modules.fs.mibif import MIBIF
   from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as lda
   
   sf = csp()
   fe = logpower
   fs = MIBIF(8, clf=lda())
   clf = lda()
   
   pos_folding = {
       'sf': {sf, ()},
       'fe': {fe, ()},
       'fs': {fs, ()},
       'clf': {clf, ()}
   }

5. Running the Pipeline
------------------------

Now we just need to run the pipeline with k-fold cross-validation. We define
the window of study starting 0.5 seconds after the cue:

.. code-block:: python

   from bciflow.modules.core.kfold import kfold
   
   results = kfold(
       target=dataset,
       start_window=dataset['events']['cue'][0] + 0.5,
       pre_folding=pre_folding,
       pos_folding=pos_folding
   )

6. Displaying Raw Results
---------------------------

Display a table of the results:

.. code-block:: python

   print(results)

7. Analyzing Performance Metrics
---------------------------------

To better visualize the processed data, we can calculate the accuracy:

.. code-block:: python

   import pandas as pd
   from bciflow.modules.analysis.metric_functions import accuracy
   
   df = pd.DataFrame(results)
   acc = accuracy(df)
   
   print(f"Accuracy: {acc:.4f}")

8. Complete Pipeline Code
---------------------------

Here is the entire pipeline code:

.. code-block:: python

   from bciflow.datasets.CBCIC import cbcic
   from bciflow.modules.core.kfold import kfold
   from bciflow.modules.tf.filterbank import filterbank
   from bciflow.modules.sf.csp import csp
   from bciflow.modules.fe.logpower import logpower
   from bciflow.modules.fs.mibif import MIBIF
   from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as lda
   import pandas as pd
   from bciflow.modules.analysis.metric_functions import accuracy
   
   dataset = cbcic(subject=1, path='data/cbcic/')
   
   pre_folding = {'tf': {filterbank, {'kind_bp': 'chebyshevII'}}}
   
   sf = csp()
   fe = logpower
   fs = MIBIF(8, clf=lda())
   clf = lda()
   
   pos_folding = {
       'sf': {sf, ()},
       'fe': {fe, ()},
       'fs': {fs, ()},
       'clf': {clf, ()}
   }
   
   results = kfold(
       target=dataset,
       start_window=dataset['events']['cue'][0] + 0.5,
       pre_folding=pre_folding,
       pos_folding=pos_folding
   )
   
   df = pd.DataFrame(results)
   acc = accuracy(df)
   print(f"Accuracy: {acc:.4f}")

.. note::
   The pipeline structure makes the analysis reproducible, standardized, and automated. Feel free to experiment by changing parameters or modules to explore new approaches.