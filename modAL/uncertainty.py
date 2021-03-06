"""
Uncertainty measures and uncertainty based sampling strategies for the active learning models.
"""

import numpy as np
from scipy.stats import entropy
from modAL.utils.selection import multi_argmax


def classifier_uncertainty(classifier, X, **predict_proba_kwargs):
    """
    Classification uncertainty of the classifier for the provided samples.

    :param classifier:
        The classifier for which the uncertainty is to be measured.
    :type classifier:
        sklearn classifier object, for instance sklearn.ensemble.RandomForestClassifier

    :param X:
        The samples for which the uncertainty of classification is to be measured.
    :type X:
        numpy.ndarray of shape (n_samples, n_features)

    :param predict_proba_kwargs:
        Keyword arguments to be passed for the predict_proba method of the classifier.
    :type predict_proba_kwargs:
        keyword arguments

    :returns:
      - **uncertainty** *(numpy.ndarray of shape (n_samples, ))* --
        Classifier uncertainty, which is 1 - P(prediction is correct).
    """
    # calculate uncertainty for each point provided
    classwise_uncertainty = classifier.predict_proba(X, **predict_proba_kwargs)

    # for each point, select the maximum uncertainty
    uncertainty = 1 - np.max(classwise_uncertainty, axis=1)
    return uncertainty


def classifier_margin(classifier, X, **predict_proba_kwargs):
    """
    Classification margin uncertainty of the classifier for the provided samples.
    This uncertainty measure takes the first and second most likely predictions
    and takes the difference of their probabilities, which is the margin.

    :param classifier:
        The classifier for which the uncertainty is to be measured
    :type classifier:
        sklearn classifier object, for instance sklearn.ensemble.RandomForestClassifier

    :param X:
        The samples for which the uncertainty of classification is to be measured
    :type X:
        numpy.ndarray of shape (n_samples, n_features)

    :param predict_proba_kwargs:
        Keyword arguments to be passed for the predict_proba method of the classifier
    :type predict_proba_kwargs:
        keyword arguments

    :returns:
      - **margin** *(numpy.ndarray of shape (n_samples, ))* --
        Margin uncertainty, which is the difference of the probabilities of first
        and second most likely predictions.
    """
    classwise_uncertainty = classifier.predict_proba(X, **predict_proba_kwargs)

    if classwise_uncertainty.shape[1] == 1:
        return np.zeros(shape=(classwise_uncertainty.shape[0],))

    part = np.partition(-classwise_uncertainty, 1, axis=1)
    margin = - part[:, 0] + part[:, 1]

    return margin


def classifier_entropy(classifier, X, **predict_proba_kwargs):
    """
    Entropy of predictions of the for the provided samples.

    :param classifier:
        The classifier for which the prediction entropy is to be measured.
    :type classifier:
        sklearn classifier object, for instance sklearn.ensemble.RandomForestClassifier

    :param X:
        The samples for which the prediction entropy is to be measured.
    :type X:
        numpy.ndarray of shape (n_samples, n_features)

    :param predict_proba_kwargs:
        Keyword arguments to be passed for the predict_proba method of the classifier.
    :type predict_proba_kwargs:
        keyword arguments

    :returns:
      - **entr** *(numpy.ndarray of shape (n_samples, ))* --
        Entropy of the class probabilities.
    """
    classwise_uncertainty = classifier.predict_proba(X, **predict_proba_kwargs)
    return np.transpose(entropy(np.transpose(classwise_uncertainty)))


def uncertainty_sampling(classifier, X, n_instances=1, **uncertainty_measure_kwargs):
    """
    Uncertainty sampling query strategy. Selects the least sure instances for labelling.

    :param classifier:
        The classifier for which the labels are to be queried.
    :type classifier:
        sklearn classifier object, for instance sklearn.ensemble.RandomForestClassifier

    :param X:
        The pool of samples to query from.
    :type X:
        numpy.ndarray of shape (n_samples, n_features)

    :param n_instances:
        Number of samples to be queried.
    :type n_instances:
        int

    :param uncertainty_measure_kwargs:
        Keyword arguments to be passed for the uncertainty measure function.
    :type uncertainty_measure_kwargs:
        keyword arguments

    :returns:
      - **query_idx** *(numpy.ndarray of shape (n_instances, ))* --
        The indices of the instances from X chosen to be labelled.
      - **X[query_idx]** *(numpy.ndarray of shape (n_instances, n_features))* --
        The instances from X chosen to be labelled.
    """
    uncertainty = classifier_uncertainty(classifier, X, **uncertainty_measure_kwargs)
    query_idx = multi_argmax(uncertainty, n_instances=n_instances)

    return query_idx, X[query_idx]


def margin_sampling(classifier, X, n_instances=1, **uncertainty_measure_kwargs):
    """
    Margin sampling query strategy. Selects the instances where the difference between
    the first most likely and second most likely classes are the smallest.

    :param classifier:
        The classifier for which the labels are to be queried.
    :type classifier:
        sklearn classifier object, for instance sklearn.ensemble.RandomForestClassifier

    :param X:
        The pool of samples to query from.
    :type X:
        numpy.ndarray of shape (n_samples, n_features)

    :param n_instances:
        Number of samples to be queried.
    :type n_instances:
        int

    :param uncertainty_measure_kwargs:
        Keyword arguments to be passed for the uncertainty measure function.
    :type uncertainty_measure_kwargs:
        keyword arguments

    :returns:
      - **query_idx** *(numpy.ndarray of shape (n_instances, ))* --
        The indices of the instances from X chosen to be labelled.
      - **X[query_idx]** *(numpy.ndarray of shape (n_instances, n_features))* --
        The instances from X chosen to be labelled.
    """
    margin = classifier_margin(classifier, X, **uncertainty_measure_kwargs)
    query_idx = multi_argmax(-margin, n_instances=n_instances)

    return query_idx, X[query_idx]


def entropy_sampling(classifier, X, n_instances=1, **uncertainty_measure_kwargs):
    """
    Entropy sampling query strategy. Selects the instances where the class probabilities
    have the largest entropy.

    :param classifier:
        The classifier for which the labels are to be queried.
    :type classifier:
        sklearn classifier object, for instance sklearn.ensemble.RandomForestClassifier

    :param X:
        The pool of samples to query from.
    :type X:
        numpy.ndarray of shape (n_samples, n_features)

    :param n_instances:
        Number of samples to be queried.
    :type n_instances:
        int

    :param uncertainty_measure_kwargs:
        Keyword arguments to be passed for the uncertainty measure function.
    :type uncertainty_measure_kwargs:
        keyword arguments

    :returns:
      - **query_idx** *(numpy.ndarray of shape (n_instances, ))* --
        The indices of the instances from X chosen to be labelled.
      - **X[query_idx]** *(numpy.ndarray of shape (n_instances, n_features))* --
        The instances from X chosen to be labelled.
    """
    entropy = classifier_entropy(classifier, X, **uncertainty_measure_kwargs)
    query_idx = multi_argmax(entropy, n_instances=n_instances)

    return query_idx, X[query_idx]
