#!/usr/bin/env python

from distutils.core import setup

setup(name='ledger-compliance-py',
      version='0.2',
      description='Python SDK for codenotary Ledger Compliance',
      author='vChain',
      url='https://github.com/vchain-us/ledger-compliance-py',
      packages=['LedgerCompliance', 'LedgerCompliance.schema',],
      install_requires=[
        'grpcio>=1.26.0',
        'dataclasses>=0.6',
        'protobuf>=3.13.0',
        'google-api>=0.1.12',
        'google-api-core>=1.22.0'
        ])
