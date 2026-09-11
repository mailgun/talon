from __future__ import absolute_import
from talon.signature import EXTRACTOR_FILENAME, EXTRACTOR_DATA
from talon.signature.learning.classifier import train, init


def train_model():
    """ retrain model and persist """
    train(init(), EXTRACTOR_DATA, EXTRACTOR_FILENAME)

if __name__ == "__main__":
    train_model()
