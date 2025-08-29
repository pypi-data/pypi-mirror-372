.. _fe:
==================================
Feature Extraction
==================================
Feature extraction is a crucial step in BCI pipelines, where meaningful 
information is derived from raw EEG signals. This process transforms 
high-dimensional data into a lower-dimensional representation, capturing 
essential patterns for classification or analysis.

.. toctree::
   :maxdepth: 1
   :caption: Classes

   bciflow.modules.fe.apsd
   bciflow.modules.fe.curvelength
   bciflow.modules.fe.logpower
   bciflow.modules.fe.nonlinearenergy
   bciflow.modules.fe.welch_period
