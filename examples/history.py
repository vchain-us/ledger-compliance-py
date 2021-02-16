#!/usr/bin/env python3

API="qervegelclrmbvcdhpvvmebpnyxgjknysayt"
HOST="172.31.255.30"
PORT=80
SECURE=False

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

KEY="LC_history".encode('ascii')
for i in range(0,10):
	cli.set(KEY, get_random_string(16).encode('ascii'))

ret=cli.history(KEY)
for h in ret:
	print("{:d}: {:s}".format(h.index, h.value.decode('ascii')))
