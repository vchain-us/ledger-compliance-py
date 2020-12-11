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
A Ledger Compliance instance must be up and running. You need IP address, port (usually 80) of the Ledger Compliance grpc service.
You'll also need an API key, which can easly be generated within the Ledger Compliance.

This library only run with python3, and it's tested with python 3.8.

## Installation

A Makefile is provided. To install the library, simply clone the repository, change to the **src** directory and launch
```make init``` to install (via pip) all the needed dependencies, followed by a ```make install``` to install the library.
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
host="cnlcserver.address.com"
port=443

client=LedgerCompliance.client.Client(apikey,host,port)
client.connect()
```

You must have a valid certificate in order to use the recommended HTTPS protocol.
You can also use **insecure (HTTP) protocol**: don't do that in production, but avoid having to setup a valid certificate.

```python
import LedgerCompliance.client

apikey="fgyozystagmmfalppyttvlqxyuwawgdwmmsd"
host="cnlcserver.address.com"
port=80

client=LedgerCompliance.client.Client(apikey,host,port, secure=False)
client.connect()
```

### Using self-signed certificates

If you have your own CA, or self-signed certificate, you can use ''set_credentials'' method to set the CA root certificate.
Keep in mind that python grpc ssl library always checks if hostname is matching the certificates, so if you are using an ip address as hostname, that IP must be in the certificate's SAN names. In alternative, you can define add an entry in the /etc/hosts file and use that name as hostname.


### Using get/set to store/retrieve data

Once the connection is in place, you can use the ```set``` method to store key/value pairs, and the ```get``` method to
retrieve the data:

```python
client.set(b"key", b"value")
value=client.get(b"key")
```
Please note that the value is serialized with a timestamp, so you can always tell when the insert was made.

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

### Batch set/get
If you need to quickly insert or retrieve many values, you can call the batch set and get methods. Batch operation are tipically orders of magnitude faster than multiple scalar inserts.

The setBatch has a dictionary as a parameters: simply fill the dict with you key/values pair and call setBatch to have it safely stored. Please note that both the keys and the values have to be bytes array.
```python
manyvalues={}
for j in range(0,100):
	k="KEY_"+get_random_string(8)
	v="VALUE_"+get_random_string(64)
	manyvalues[k.encode('ascii')]=v.encode('ascii')
client.setBatch(manyvalues)
```

To retrieve multiple values, populate an array with wanted keys, then call getBatch:
```python
keys=[b"key1", b"key2"]
client.getBatch(keys)
```

### Scan
You can scan LC database by prefix, getting keys (and values) based on a given prefix of the key. For this, use method scan.

```python
client.scan(prefix, offset, limit, reverse, deep)
```
The method return a list of key/values having `prefix` as key prefix. Offset and limit are used to ket only a subset (for paginating large arrays); the boolean reverse is used to specify sorting.

### History

To get the history of updates to a key, use `history` method: given a key, returns a list of all subsequent modification, each with timestamp and index.
```python
print(client.History(b"key1"))
```

### Multithreading / multiprocessing
The library is not reentrant. If used in a multiprocess application, each running process must have its own instance.
