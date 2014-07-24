from talon.quotations import register_xpath_extensions
from talon import signature


def init():
    register_xpath_extensions()
    signature.initialize()
