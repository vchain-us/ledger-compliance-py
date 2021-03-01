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

This library only run with python3, and it's tested with python 3.8. This library requires the dataclasses module, which is part of the basic python library starting with python 3.7. You can still use python 3.6 if you install the dataclasses pypi module.

## Installation

### Using PYPI:

You can easily install ledger-compliance-py using pip:
```python
pip install ledger-compliance-py
```

### From source:

A Makefile is provided. To install the library, simply clone the repository, change to the **src** directory and launch
```make init``` to install (via pip) all the needed dependencies, followed by a ```make install``` to install the library.
A python virtual environment is raccomanded.


## Supported Versions

This version supports CodeNotary Ledger Compliance version 2.1.5+
Use python 3.7+, or python 3.6 with dataclasses module.

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
Here ```value``` is a dataclass holding informations extracted from the database: the trasaction id, its key (useful when you ask for a reference) and of course the value. If you just need the value of a key, you can use ```getValue``` method which just retrieve the value.

### Encoding
To avoid encoding issues, both key and value are byte array, not string. You have to ```encode``` the data before writing and ```decode``` after reading.

### Verified read/write

The real strength of the Ledger Compliance is the proof that the data is not been tampered.
The ''verified'' version of ```get``` and ```set``` are designed 
to verify, client side, the proof returned by the server.

To safely store a key/value pair, simply call the ```verifiedSet``` method.
The returned value has a field (called ```verified```) which testify the 
correctness of the insert. Actually, the SDK computes, client side, all the merkele tree hashes that the server computed
when inserting, and then matches the results.
So the appliaction has the proof that the server insert was made without tampering.
In the same way, the ```verifiedGet``` guarantees that the returned data has not been tampered with.

```python
resp=client.verifiedSet(b"key",  b"value")
if resp.verified:
    print("Data correctly stored at transaction:",resp.txid)
 
resp=client.verifiedGet(b"key")
if resp.verified:
    print("Value is:",resp.value,"at transaction:",resp.txid)
```
Since indexing process is asynchronous, inserted values can be unavailable until indexed.
If you know the transaction id in which the key is contained, you can specify that value in the verifiedGet. The call will
block until that transaction is indexed so that the value can be safely retrieved:

```python
resp=client.verifiedSet(b"key",  b"value")
resp=client.verifiedGet(b"key", resp.txid)
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
As with simple (not batched) get, you get a dataclass holding the key and the transaction for each requested key.
You can use getValueBatch if you just want back the vaules: it returns a dictionary of key holding the corrisponding values.

### Scan
You can scan LC database by prefix, getting keys (and values) based on a given prefix of the key. For this, use method scan.

```python
client.scan(seekKey, prefix, desc, limit, sinceTx, noWait)
```
The method return a list of key/values/tx having `prefix` as key prefix, starting from `seekKey`. seekkey and limit are used to ket only a subset (for paginating large arrays); the boolean `desc` is used to specify descending ordering.

### History

To get the history of updates to a key, use `history` method: given a key, returns a list of all subsequent modification, each with timestamp and index.
```python
print(client.History(b"key1"))
```
## State persistance

An important LC feature is the ability for a client to check every transaction for tampering. In order to 
be able to do that, it is necessary to persist client state (i.e., save it to disk) so that if some tampering 
on the server happens between two runs, it is immediatly detected.

A `RootService` implements just that: it stores immudb client after every transaction, in order to be able to
use it afterward to check the server correctness.

### Using the Persistent Root Service

The default RootService, for simplicity, commits the state to RAM, and so it is unsuitable for real time safe
application. To have persistance, the application must instantiate a `PersistentRootService` object, which stores
its state to disk, and use it in the `connect` method.

Let's see a simple example that uses state persistance:

```python
from LedgerCompliance.stateservice import PersistentRootService
from LedgerCompliance import client as LCClient
client=LCClient(apikey,host,port)
client.connect(PersistentRootService())
client.verifiedGet(b"example")
```

In this example, the Root Service is saved to the disk after every verified transaction. As you can see, it is very
easy to use. Just create and use the PersistentRootService object in the client connection.

### Process and threads

Please keep in mind that the implementation is not thread/process safe. If you are using a multi-process application,
it is advisable to use a different state file for every instance: just pass the filename as argument to the 
PersistentRootService constructor:

```python
client.connect(PersistentRootService("statefilename"))
```

Default rootfile is "~/.cnlcRoot"

If needed/wanted, it is also easy to extend the default implementation adding synchronization primitives to the get/set methods.
In this way, more than one immudb client can share the same PersistentRootService instance without interering each other.

## Multithreading / multiprocessing
The library is not reentrant. If used in a multiprocess application, each running process must have its own instance.
