# -*- coding: utf-8 -*-

"""The module's functions could init, train, save and load a classifier.
The classifier could be used to detect if a certain line of the message
body belongs to the signature.
"""

from __future__ import absolute_import

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
    except Exception:
        import sys
        if sys.version_info > (3, 0):
            return load_compat(saved_classifier_filename)

        raise


def load_compat(saved_classifier_filename):
    import os
    import pickle
    import tempfile

    # we need to switch to the data path to properly load the related _xx.npy files
    cwd = os.getcwd()
    os.chdir(os.path.dirname(saved_classifier_filename))

    # convert encoding using pick.load and write to temp file which we'll tell joblib to use
    pickle_file = open(saved_classifier_filename, 'rb')
    classifier = pickle.load(pickle_file, encoding='latin1')

    try:
        # save our conversion if permissions allow
        joblib.dump(classifier, saved_classifier_filename)
    except Exception:
        # can't write to classifier, use a temp file
        tmp = tempfile.SpooledTemporaryFile()
        joblib.dump(classifier, tmp)
        saved_classifier_filename = tmp

    # important, use joblib.load before switching back to original cwd
    jb_classifier = joblib.load(saved_classifier_filename)
    os.chdir(cwd)

    return jb_classifier
