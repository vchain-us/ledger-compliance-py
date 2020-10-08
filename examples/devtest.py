#!/usr/bin/env python

import LedgerCompliance.client

apikey="jaxozystagmmfalupyttvlqxyuwawgdtldsd"
host="172.31.255.10"
port=3324

a=LedgerCompliance.client.Client(apikey,host,port)
print(a.connect())

print(a.set(b"gorilla",b"banana"))
print(a.get(b"gorilla"))

print(a.safeSet(b"happy",b"hippo"))
print(a.safeGet(b"happy"))
