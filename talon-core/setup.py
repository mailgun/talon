from __future__ import absolute_import
from setuptools import setup, find_packages


setup(name='talon-core',
      version='1.6.0',
      description=("Mailgun library "
                   "to extract message quotations and signatures."),
      long_description=open("README.rst").read(),
      author='Mailgun Inc.',
      author_email='admin@mailgunhq.com',
      url='https://github.com/mailgun/talon',
      license='APACHE2',
      packages=find_packages(exclude=['tests', 'tests.*']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          "lxml",
          "regex",
          "chardet",
          "cchardet",
          "cssselect",
          "six",
          "html5lib",
          "joblib",
          ],
      tests_require=[
          "mock",
          "nose",
          "coverage"
          ]
      )
