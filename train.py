from __future__ import absolute_import
from talon.signature import EXTRACTOR_FILENAME, EXTRACTOR_DATA
from talon.signature.learning.classifier import train, init, train_withcv
from datetime import datetime


def train_model():
    """ retrain model and persist """
    train(init(), EXTRACTOR_DATA, EXTRACTOR_FILENAME)

def train_model_properly():
    """ retrain model with nested cross validation and persist """
    classifier_filename = EXTRACTOR_FILENAME + "_rbf_svm_" + str(datetime.now())
    train_withcv(EXTRACTOR_DATA, classifier_filename, classifier_choice="rbf svm", test_type='test')

if __name__ == "__main__":
    train_model_properly()

