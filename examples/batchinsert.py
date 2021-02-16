#!/usr/bin/env python3

API="acpkrvlnhttowqmraisvzndfiyojsoymgcdy"
HOST="172.31.255.10"
PORT=80
SECURE=False
BATCHSIZE=500
NUM=120

import LedgerCompliance.client
import string
import random
import time

cli=LedgerCompliance.client.Client(API, HOST, PORT, SECURE)
cli.connect()

def get_random_string(length):
    letters = string.ascii_lowercase
    ret = ''.join(random.choice(letters) for i in range(length))
    return ret

print("Generating")
manyvalues=[]
for i in range(0,NUM):
	manyvalues.append({})
	for j in range(0,BATCHSIZE):
		k="KEY_"+get_random_string(8)
		v="VALUE_"+get_random_string(64)
		manyvalues[i][k.encode('ascii')]=v.encode('ascii')
print("Starting insert")
t0=time.time()
for i in range(0,NUM):
	cli.setBatch(manyvalues[i])
t1=time.time()
if t1!=t0:
	insert_sec=(BATCHSIZE*NUM)/(t1-t0)
else:
	insert_sec=0 # avoid dividing per zero
print("Inserted {} values in {:.3f} seconds {:.3f} insert/s".format(BATCHSIZE*NUM, t1-t0, insert_sec))


