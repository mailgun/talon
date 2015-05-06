from setuptools import setup, find_packages


setup(name='talon',
      version='1.0.2',
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
          "lxml==2.3.3",
          "regex>=1",
          "html2text",
          "nose>=1.2.1",
          "numpy",
          "mock",
          "coverage",
          "scipy",
          "scikit-learn==0.16.1", # pickled versions of classifier, else rebuild
          ]
      )
