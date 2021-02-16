#!/usr/bin/env python

import LedgerCompliance.client

apikey="jaxozystagmmfalupyttvlqxyuwawgdtldsd"
host="172.31.255.10"
port=80
tls=False
a=LedgerCompliance.client.Client(apikey,host,port,tls) 
print(a.connect())

print(a.set(b"gorilla",b"banana"))
print(a.get(b"gorilla"))

print(a.verifiedSet(b"happy",b"hippo"))
print(a.verifiedGet(b"happy"))
