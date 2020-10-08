# ledger-compliance-py
## Official Python SDK for interacting with CodeNotary Ledger Compliance.

## Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Supported Versions](#supported-versions)
- [Quickstart](#quickstart)
- [Step by step guide](#step-by-step-guide)

## Introduction
ledger-compliance-py implements a [grpc] Ledger Compliance client. A minimalist API is exposed for applications while cryptographic
verifications and state update protocol implementation are fully implemented by this client.

[grpc]: https://grpc.io/

## Prerequisites
A Ledger Compliance instance must be up and running. You need IP address, port (usually 3324) of the Ledger Compliance grpc service.
You'll also need an API key, which can easly be generated within the Ledger Compliance.

This library only run with python3, and it's tested with python 3.8.

## Installation

A Makefile is provided. To install the library, simply clone the repository and launch
```make init``` to install (via pip) all the needed dependencies, followed by a ``make install``` to install the library.
A python virtual environment is raccomanded.

## Supported Versions

TBD

## Quickstart

## Step by step guide
