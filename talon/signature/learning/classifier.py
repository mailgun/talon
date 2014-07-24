# -*- coding: utf-8 -*-

"""The module's functions could init, train, save and load a classifier.
The classifier could be used to detect if a certain line of the message
body belongs to the signature.
"""

import os
import sys

from PyML import SparseDataSet, SVM


def init():
    '''Inits classifier with optimal options.'''
    return SVM(C=10, optimization='liblinear')


def train(classifier, train_data_filename, save_classifier_filename=None):
    '''Trains and saves classifier so that it could be easily loaded later.'''
    data = SparseDataSet(train_data_filename, labelsColumn=-1)
    classifier.train(data)
    if save_classifier_filename:
        classifier.save(save_classifier_filename)
    return classifier


def load(saved_classifier_filename, train_data_filename):
    """Loads saved classifier.

    Classifier should be loaded with the same data it was trained against
    """
    train_data = SparseDataSet(train_data_filename, labelsColumn=-1)
    classifier = init()
    classifier.load(saved_classifier_filename, train_data)
    return classifier
