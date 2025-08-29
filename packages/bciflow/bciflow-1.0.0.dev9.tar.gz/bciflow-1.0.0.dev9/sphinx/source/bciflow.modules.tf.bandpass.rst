.. _bandpass:
===========================
Bandpass Filtering
===========================
Bandpass filtering is a technique used to isolate specific frequency 
ranges within a signal. In the context of EEG data, bandpass filters 
are essential for extracting frequency bands of interest, such as alpha 
(8-12 Hz), beta (12-30 Hz), or gamma (30-50 Hz), while attenuating 
frequencies outside the desired range.

.. toctree::
   :maxdepth: 1
   :caption: Versions

   bciflow.modules.tf.bandpass.chebyshevII
   bciflow.modules.tf.bandpass.convolution
For more details on bandpass filtering, refer to:
   - Oppenheim, A. V., & Schafer, R. W. (2010). *Discrete-Time Signal Processing*. Pearson.
   - Smith, S. W. (1997). *The Scientist and Engineer's Guide to Digital Signal Processing*. California Technical Publishing.