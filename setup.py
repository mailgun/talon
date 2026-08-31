from __future__ import absolute_import
from setuptools import setup, find_packages
from setuptools.command.install import install


class InstallCommand(install):
    user_options = install.user_options + [
        ('no-ml', None, "Don't install without Machine Learning modules."),
    ]

    boolean_options = install.boolean_options + ['no-ml']

    def initialize_options(self):
        install.initialize_options(self)
        self.no_ml = None

    def finalize_options(self):
        install.finalize_options(self)
        if self.no_ml:
            dist = self.distribution
            dist.packages=find_packages(exclude=[
                "tests",
                "tests.*",
                "talon.signature",
                "talon.signature.*",
            ])
            for not_required in ["numpy", "scipy", "scikit-learn==0.24.1"]:
                dist.install_requires.remove(not_required)


setup(name='talon',
      version='1.6.0',
      description=("Mailgun library "
                   "to extract message quotations and signatures."),
      long_description=open("README.rst").read(),
      author='Mailgun Inc.',
      author_email='admin@mailgunhq.com',
      url='https://github.com/mailgun/talon',
      license='APACHE2',
      cmdclass={
          'install': InstallCommand,
      },
      packages=find_packages(exclude=['tests', 'tests.*']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          "lxml",
          "regex",
          "numpy",
          "scipy",
          "scikit-learn>=1.0.0",
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
