# -*- coding: utf-8 -*-

"""The module's functions could init, train, save and load a classifier.
The classifier could be used to detect if a certain line of the message
body belongs to the signature.
"""

from numpy import genfromtxt
import joblib
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
    """Loads saved classifier."""
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
    original_dir = os.path.dirname(saved_classifier_filename)
    os.chdir(original_dir)

    # convert encoding using pick.load and write to temp file which we'll tell joblib to use
    pickle_file = open(
        os.path.basename(saved_classifier_filename), "rb"
    )  # Use basename here
    classifier = pickle.load(pickle_file, encoding="latin1")
    pickle_file.close()  # Close the file

    temp_joblib_file_path = None
    try:
        # save our conversion if permissions allow
        joblib.dump(classifier, os.path.basename(saved_classifier_filename))
        # Use the original path for joblib.load if dump was successful
        path_for_joblib_load = os.path.basename(saved_classifier_filename)
    except Exception as e_dump:
        # can't write to classifier, use a temp file
        # Create a named temporary file for joblib to read from, as SpooledTemporaryFile might not have a name attribute
        # and joblib.load often expects a filename string or a file object with a name.
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".joblib", dir="."
        ) as tmp_file_obj:  # dir='.' to be in current (data) dir
            temp_joblib_file_path = tmp_file_obj.name
            joblib.dump(classifier, tmp_file_obj)
        path_for_joblib_load = temp_joblib_file_path

    # important, use joblib.load before switching back to original cwd
    jb_classifier = joblib.load(path_for_joblib_load)

    if temp_joblib_file_path:
        try:
            os.remove(temp_joblib_file_path)
        except OSError as e_remove:
            pass  # If removal fails, it's not critical for function's main purpose

    os.chdir(cwd)

    return jb_classifier
