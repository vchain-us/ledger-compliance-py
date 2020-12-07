#!/usr/bin/env python

import LedgerCompliance.client

apikey="hpkqcnqdtcmgudfuuyfshnvsmfnwiyleajcq"
host="ppp.immudb.io"
port=33443

a=LedgerCompliance.client.Client(apikey,host,port,True)
a.set_credentials()
a.connect()
#print(a.set(b"gorilla",b"banana"))
#print(a.get(b"gorilla"))
#print(a.safeSet(b"dodge",b"viper"))
#print(a.safeGet(b"dodge"))
print(a.currentRoot())
print(a.safeSet(b"gorilla2",b"banana2"))
#kv={b'k1':b'v1', b'k2':b'v2'}
#print(a.setBatch(kv))
#kk=[b'k1', b'k2']
#print(a.getBatch(kk))
#print(a.scan(b'k', b'', 0, False, False))
#print(a.history(b"gorilla"))
