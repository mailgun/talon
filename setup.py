import os
import sys
import contextlib

from distutils.spawn import find_executable
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
          "lxml==3.3.1",
          "regex==0.1.20110315",
          "chardet==1.0.1",
          "dnspython==1.11.1",
          "html2text",
          "nose==1.3.1",
          "numpy==1.6.1",
          "mock",
          "coverage",
          "flanker"
          ]
      )


def install_pyml():
    '''
    Downloads and installs PyML
    '''
    try:
        import PyML
    except:
        pass
    else:
        return

    pyml_tarball = (
        'http://garr.dl.sourceforge.net/project/pyml/PyML-0.7.13.3.tar.gz')
    pyml_srcidr = 'PyML-0.7.13.3'

    # see if PyML tarball needs to be fetched:
    if not dir_exists(pyml_srcidr):
        run("curl %s | tar -xz" % pyml_tarball)

    # compile&install:
    with cd(pyml_srcidr):
        python('setup.py build')
        python('setup.py install')


def run(command):
    if os.system(command) != 0:
        raise Exception("Failed '{}'".format(command))
    else:
        return 0


def python(command):
    command = '{} {}'.format(sys.executable, command)
    run(command)


def enforce_executable(name, install_info):
    if os.system("which {}".format(name)) != 0:
        raise Exception(
            '{} utility is missing.\nTo install, run:\n\n{}\n'.format(
                name, install_info))


def pip(command):
    command = '{} {}'.format(find_executable('pip'), command)
    run(command)


def dir_exists(path):
    return os.path.isdir(path)


@contextlib.contextmanager
def cd(directory):
    curdir = os.getcwd()
    try:
        os.chdir(directory)
        yield {}
    finally:
        os.chdir(curdir)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ['develop', 'install']:
        enforce_executable('curl', 'sudo aptitude install curl')

        install_pyml()
