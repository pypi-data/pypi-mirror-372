"""
Description
-----------

This module contains the functions to calculate the metrics accuracy, Cohen's
kappa coefficient, logarithmic loss and root-mean-squared error. These
functions are used to evaluate the performance of the given data.
"""

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    log_loss,
    root_mean_squared_error,
)


def accuracy(results: pd.DataFrame) -> float:
    """Calculates the accuracy given the correct labels and the predicted
    probabilities.

    Parameters
    ----------
    results : pandas.DataFrame
            Dataframe with the true label and predicted probabilities.

    Returns
    -------
    float
            Accuracy value.

    """
    correct = results['true_label']
    probs = results.iloc[:, 3:]
    return accuracy_score(correct, probs.idxmax(axis=1))


def kappa(results: pd.DataFrame) -> float:
    """Calculates the Cohen's kappa coefficient given the correct labels and
    the predicted probabilities.

    Parameters
    ----------
    results : pandas.DataFrame
            Dataframe with the true label and predicted probabilities.

    Returns
    -------
    float
            Kappa value

    """
    correct = results['true_label']
    probs = results.iloc[:, 3:]
    return cohen_kappa_score(correct, probs.idxmax(axis=1))


def logloss(results: pd.DataFrame) -> float:
    """Calculates the logarithmic loss given the correct labels and the
    predicted probabilities.

    Parameters
    ----------
    results : pandas.DataFrame
            Dataframe with the true label and predicted probabilities.

    Returns
    -------
    float
            Logarithmic loss value.

    """
    correct = results['true_label']
    probs = results.iloc[:, 3:]
    return log_loss(correct, probs, labels=probs.columns)


def rmse(results: pd.DataFrame) -> float:
    """Calculates the root-mean-squared error given the correct labels and the
    predicted probabilities.

    Parameters
    ----------
    results : pandas.DataFrame
            Dataframe with the true label and predicted probabilities.

    Returns
    -------
    float
            Root-mean-squared error value.

    """
    correct = results['true_label']
    probs = results.iloc[:, 3:]
    return root_mean_squared_error(pd.get_dummies(correct), probs)
