# ledger-compliance-py [![License](https://img.shields.io/github/license/codenotary/immudb4j)](LICENSE)
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

A simple example is provided in the "examples" subdirectory.

## Step by step guide

### Creating the client
The first step is to instantiate a LC client. You only need one ''API Key'', and the IP address (and the port) of the Ledger Compliance Server.

```python
import LedgerCompliance.client

apikey="fgyozystagmmfalppyttvlqxyuwawgdwmmsd"
host="192.168.199.199"
port=3324

client=LedgerCompliance.client.Client(apikey,host,port)
client.connect()
```

### Using get/set to store/retrieve data

Once the connection is in place, you can use the ```set``` method to store key/value pairs, and the ```get``` method to
retrieve the data:

```python
client.set(b"key", b"value")
value=client.get(b"key")
```

### Encoding
To avoid encoding issues, both key and value are byte array, not string. You have to ```encode``` the data before writing and ```decode``` after reading.

### Safe read/write

The real strength of the Ledger Compliance is the proof that the data is not been tampered. The ''safe'' version of ```get``` and ```set``` are designed 
to verify, client side, the proof returned by the server.

To safely store a key/value pair, simply call the ```safeSet``` method. The returned value has a field (called ```verified```) which testify the 
correctness of the insert. In the same way, the ```safeGet``` guarantees that the returned data has not been tampered with.

```python
resp=client.safeSet(b"key,  b"value")
if resp.verified:
    print("Data correctly stored ad index:",resp.index)
    print("Proof is:",resp.proof)
 
 resp=client.safeGet(b"key")
 if resp.verified:
    print("Value is:",resp.value,"at index:",resp.index)
    print("Proof is:",resp.proof)
```
### Multithreading / multiprocessing
The library is not reentrant. If used in a multiprocess application, each running process  must have its own instance.
