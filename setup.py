#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from os import path
from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='pyDigitalWaveTools',
      version='1.0',
      description='Library for operations with VCD and other digital wave files',
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Topic :: System :: Hardware",
        "Topic :: System :: Emulators",
        "Topic :: Utilities",
      ],
      url='https://github.com/Nic30/pyDigitalWaveTools',
      author='Michal Orsak',
      author_email='michal.o.socials@gmail.com',
      license='MIT',
      packages=find_packages(),
      package_data={'pyDigitalWaveTools': ['*.vcd', ]},
      include_package_data=True,
      zip_safe=False,
      tests_require=['pytest'])
