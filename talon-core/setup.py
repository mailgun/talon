from __future__ import absolute_import
from setuptools import setup, find_packages


setup(name='talon-core',
      version='1.6.1',
      description=("Mailgun library "
                   "to extract message quotations and signatures."),
      long_description=open("README.rst").read(),
      author='Mailgun Inc.',
      author_email='admin@mailgunhq.com',
      url='https://github.com/mailgun/talon',
      license='APACHE2',
      packages=find_packages(exclude=['talon_core_tests', 'talon_core_tests.*']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          "lxml",
          "regex",
          "cssselect",
          "six",
          "html5lib",
          ],
      tests_require=[
          "pytest",
          "pytest-cov"
          ]
      )
