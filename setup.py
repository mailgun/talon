from setuptools import setup, find_packages


setup(name='talon',
      version='1.2.7',
      description=("Mailgun library "
                   "to extract message quotations and signatures."),
      long_description=open("README.rst").read(),
      author='Mailgun Inc.',
      author_email='admin@mailgunhq.com',
      url='https://github.com/mailgun/talon',
      license='APACHE2',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          "lxml>=2.3.3",
          "regex>=1",
          "numpy",
          "scipy",
          "scikit-learn==0.16.1", # pickled versions of classifier, else rebuild
          'chardet>=1.0.1',
          'cchardet>=0.3.5',
          'cssselect'
          ],
      tests_require=[
          "mock",
          "nose>=1.2.1",
          "coverage"
          ]
      )
