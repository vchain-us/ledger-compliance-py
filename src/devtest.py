#!/usr/bin/env python

import LedgerCompliance.client

apikey="dwquppzqfqgvvzpfledoldopkxuhiciicupa"
host="172.31.255.10"
port=33080

a=LedgerCompliance.client.Client(apikey,host,port,False)
#with open("/home/simone/dl/lc-vchain-us.pem","rb") as f:
#	a.set_credentials(root_certificates=f.read())
a.connect()
#print(a.set(b"gorilla",b"banana"))
#print(a.get(b"gorilla"))
#print(a.safeSet(b"dodge",b"viper"))
#print(a.safeGet(b"dodge"))
#print(a.currentState())
print(a.verifiedGet(b"gorilla2"))
print(a.verifiedSet(b"hello",b'world'))

#kv={b'k1':b'v1', b'k2':b'v2'}
#print(a.setBatch(kv))
#kk=[b'k1', b'k2']
#print(a.getBatch(kk))
#print(a.scan(b'k', b'', 0, False, False))
#print(a.history(b"gorilla"))
