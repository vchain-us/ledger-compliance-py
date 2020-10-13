#!/usr/bin/env python3

API="aaxjavjuvpfvwkioewfmgspuvribgwpkacng"
HOST="172.31.255.10"
PORT=3324
NUM=100

import LedgerCompliance.client
import string
import random
import time

cli=LedgerCompliance.client.Client(API, HOST, PORT)
cli.connect()

def get_random_string(length):
    letters = string.ascii_lowercase
    ret = ''.join(random.choice(letters) for i in range(length))
    return ret

print("Generating")
manyvalues=[]
for i in range(0,NUM):
	k="KEY_"+get_random_string(8)
	v="VALUE_"+get_random_string(64)
	manyvalues.append((k.encode('ascii'),v.encode('ascii')))
print("Starting insert")
t0=time.time()
for i in range(0,NUM):
	cli.safeSet(manyvalues[i][0],manyvalues[i][1])
t1=time.time()
if t1!=t0:
	insert_sec=NUM/(t1-t0)
else:
	insert_sec=0 # avoid dividing per zero
print("Inserted {} values in {:.3f} seconds {:.3f} insert/s".format(NUM, t1-t0, insert_sec))


