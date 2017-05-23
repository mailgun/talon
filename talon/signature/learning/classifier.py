# -*- coding: utf-8 -*-

"""The module's functions could init, train, save and load a classifier.
The classifier could be used to detect if a certain line of the message
body belongs to the signature.
"""

from __future__ import absolute_import

import pickle

from numpy import genfromtxt
from sklearn.externals import joblib
from sklearn.svm import LinearSVC


def init():
    """Inits classifier with optimal options."""
    return LinearSVC(C=10.0)


def train(classifier, train_data_filename, save_classifier_filename=None):
    """Trains and saves classifier so that it could be easily loaded later."""
    file_data = genfromtxt(train_data_filename, delimiter=",")
    train_data, labels = file_data[:, :-1], file_data[:, -1]
    classifier.fit(train_data, labels)

    if save_classifier_filename:
        joblib.dump(classifier, save_classifier_filename)
    return classifier


def load(saved_classifier_filename, train_data_filename):
    """Loads saved classifier. """
    try:
        return joblib.load(saved_classifier_filename)
    except ValueError:
        import sys
        kwargs = {}
        if sys.version_info > (3, 0):
            kwargs["encoding"] = "latin1"

        loaded = pickle.load(open(saved_classifier_filename, 'rb'), **kwargs)
        joblib.dump(loaded, saved_classifier_filename, compress=True)
        return joblib.load(saved_classifier_filename)
