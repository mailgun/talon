# -*- coding: utf-8 -*-

"""The module's functions could init, train, save and load a classifier.
The classifier could be used to detect if a certain line of the message
body belongs to the signature.
"""

from numpy import genfromtxt
from sklearn.svm import LinearSVC
from sklearn.externals import joblib


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
    return joblib.load(saved_classifier_filename)
