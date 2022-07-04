from setuptools import setup, find_packages
from ConfigParser import ConfigParser


# Internal Contact
# Sherub Thakur <sherub.thakur@kayako.com>

config = ConfigParser()

with open('setup.cfg') as fp:
    config.readfp(fp, 'setup.cfg')

setup(
    name=config.get('metadata', 'name'),
    description=config.get('metadata', 'description'),
    version=config.get('metadata', 'version'),
    author=config.get('metadata', 'author'),
    author_email=config.get('metadata', 'author_email'),
    packages=find_packages(),
    install_requires=[each.strip() for each in config.get('options', 'install_requires').split(';')],
    tests_require=[
        "mock",
        "nose>=1.2.1",
        "coverage",
    ],
    setup_requires=["nose>=1.0"]
)

