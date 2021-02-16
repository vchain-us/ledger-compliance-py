#!/usr/bin/env python3

API="ridkvqszuhezqlluamnhqihagjbuudfmxtht"
HOST="172.31.255.10"
PORT=80
SECURE=FALSE
NUM=100

import LedgerCompliance.client
import string
import random
import time
from multiprocessing import Process


def get_random_string(length):
    letters = string.ascii_lowercase
    ret = ''.join(random.choice(letters) for i in range(length))
    return ret

def worker(rep):
	cli=LedgerCompliance.client.Client(API, HOST, PORT, SECURE)
	cli.connect()
	for i in range(0,rep):
		msg_key="KEY_"+get_random_string(8)
		msg_val="VALUE_"+get_random_string(random.randint(50,1000))
		cli.verifiedSet(msg_key.encode(),msg_val.encode())
		res=cli.verifiedGet(msg_key.encode())
		assert res.verified

proclist=[]
for i in range(0,4):
	proclist.append(Process(target=worker, args=(100,)))
t0=time.time()
for p in proclist:    
	p.start()
for p in proclist:
	p.join()
t1=time.time()
print("Run time: {} seconds".format(t1-t0))
