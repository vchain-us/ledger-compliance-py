#!/usr/bin/env python

from setuptools import setup

with open("../README.md", "rt") as fh:
    long_description = fh.read()

setup(name='ledger-compliance-py',
      version='2.1.5-rc3',
      description='Python SDK for codenotary Ledger Compliance',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='CodeNotary',
      url='https://github.com/vchain-us/ledger-compliance-py',
      packages=['LedgerCompliance', 'LedgerCompliance.schema',],
      install_requires=[
        'grpcio>=1.26.0',
        'dataclasses>=0.6',
        'protobuf>=3.13.0',
        'google-api>=0.1.12',
        'google-api-core>=1.22.0'
        ],
      classifiers=[
              'Intended Audience :: Developers',
              'Topic :: Software Development :: Build Tools',
              "License :: OSI Approved :: Apache Software License",
              "Operating System :: OS Independent",
              'Programming Language :: Python :: 3',
              'Programming Language :: Python :: 3.6',
              'Programming Language :: Python :: 3.7',
              'Programming Language :: Python :: 3.8',
              ],
      python_requires='>=3.6',
      )
