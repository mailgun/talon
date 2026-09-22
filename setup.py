from __future__ import absolute_import
from setuptools import setup, find_packages


setup(name='talon',
      version='1.7.0',
      description=("Mailgun library "
                   "to extract message quotations and signatures."),
      long_description=open("README.rst").read(),
      author='Mailgun Inc.',
      author_email='admin@mailgunhq.com',
      url='https://github.com/mailgun/talon',
      license='APACHE2',
      classifiers=[
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.14',
          ],
      python_requires='>=3.7',
      packages=find_packages(exclude=['tests', 'tests.*']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          "lxml<6; python_version < '3.8'",
          "lxml; python_version >= '3.8'",
          "regex<2024.5.10; python_version < '3.8'",
          "regex; python_version >= '3.8'",
          "cssselect",
          "six",
          "html5lib",
          ],
      extras_require={
          "ml": [
              "numpy<1.22; python_version < '3.8'",
              "numpy; python_version >= '3.8'",
              "scipy<1.8; python_version < '3.8'",
              "scipy; python_version >= '3.8'",
              "scikit-learn>=1.0.0,<1.1; python_version < '3.8'",
              "scikit-learn>=1.0.0; python_version >= '3.8'",
              "joblib<1.4; python_version < '3.8'",
              "joblib; python_version >= '3.8'",
          ],
      },
      tests_require=[
          "pytest<8; python_version < '3.8'",
          "pytest; python_version >= '3.8'",
          "pytest-cov<5; python_version < '3.8'",
          "pytest-cov; python_version >= '3.8'",
          "coverage<7.4; python_version < '3.8'",
          ]
      )
