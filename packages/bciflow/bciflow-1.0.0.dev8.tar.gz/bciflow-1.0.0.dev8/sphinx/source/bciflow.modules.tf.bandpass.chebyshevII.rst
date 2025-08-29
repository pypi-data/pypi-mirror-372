.. _bandpass_chebyshev:
========================
Chebyshev Type II Filter
========================
.. automodule:: bciflow.modules.tf.bandpass.chebyshevII
   :members:
   :show-inheritance:
   :undoc-members:
The implementation uses the `scipy.signal.cheby2` function to design the filter and `scipy.signal.filtfilt` for zero-phase filtering.