#!/usr/bin/env python

import LedgerCompliance.client

apikey="qervegelclrmbvcdhpvvmebpnyxgjknysayt"
host="172.31.255.30"
port=3324

a=LedgerCompliance.client.Client(apikey,host,port)
a.connect()
#print(a.set(b"gorilla",b"banana"))
#print(a.get(b"gorilla"))
#print(a.safeSet(b"dodge",b"viper"))
#print(a.safeGet(b"dodge"))
print(a.currentRoot())
print(a.safeGet(b"gorilla"))
#kv={b'k1':b'v1', b'k2':b'v2'}
#print(a.setBatch(kv))
#kk=[b'k1', b'k2']
#print(a.getBatch(kk))
#print(a.scan(b'k', b'', 0, False, False))
#print(a.history(b"gorilla"))
