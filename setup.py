#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    #user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import shlex
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


setup(name='pyDigitalWaveTools',
      version='0.2',
      description='python library for operations with VCD and other digital wave files ',
      url='https://github.com/Nic30/pyDigitalWaveTools',
      author='Michal Orsak',
      author_email='michal.o.socials@gmail.com',
      license='MIT',
      packages=find_packages(),
      package_data={'pyDigitalWaveTools': ['*.vcd', ]},
      include_package_data=True,
      zip_safe=False,
      tests_require=['pytest'],
      # test_suite='pyDigitalWaveTools.tests.all.suite',
      )
