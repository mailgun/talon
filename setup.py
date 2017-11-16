from __future__ import absolute_import
from setuptools import setup, find_packages


setup(
    name='talon',
    version='1.4.6',
    description=("Mailgun library "
                 "to extract message quotations and signatures."),
    long_description=open("README.rst").read(),
    author='Kayako',
    author_email='sherub.thakur@kayako.com',
    url='https://github.com/kayako/talon',
    license='APACHE2',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        "lxml>=2.3.3",
        "html5-parser",
        "regex>=1",
        'chardet>=1.0.1',
        'cchardet>=0.3.5',
        'cssselect',
        'six>=1.10.0',
        'html5lib',
    ],
    tests_require=[
        "mock",
        "nose>=1.2.1",
        "coverage",
    ],
    setup_requires=["nose>=1.0"]
)
