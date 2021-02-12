from . import mock_lc
import pytest
import grpc

apikey="dwquppzqfqgvvzpfledoldopkxuhiciicupa"
host="172.31.255.10"
port=33080
scure=False

def test_zero():
	a=mock_lc.MockClient(apikey,host,port,scure)
	a.testname("test_zero")
	a.connect()
	a.currentState()

	
#def test_connect():
	#a=mock_lc.MockClient(apikey,host,port,secure=False)
	#a=mock_lc.MockClient(apikey,host,port,secure=True)
	#a.set_credentials()
	#try:
		#a.connect()
	#except grpc._channel._InactiveRpcError as e:
		#pass
	#a.InterceptInterceptor()
	#a.connect()
	
def test_health():
	a=mock_lc.MockClient(apikey,host,port,scure)
	a.testname("test_health")
	a.connect()
	h=a.health()
	assert h.status
	
def test_get_set():
	a=mock_lc.MockClient(apikey,host,port,scure)
	a.testname("test_set_get")
	a.connect()
	a.set(b"gorilla",b"banana")
	resp=a.get(b"gorilla")
	assert resp.value==b"banana"
	
def test_verifiedSetGet():
	a=mock_lc.MockClient(apikey,host,port,scure)
	a.testname("test_verifiedSetGet")
	a.connect()
	resp=a.verifiedSet(b"dodge",b"viper")
	resp=a.verifiedGet(b"gorilla")
	assert resp.verified

	
def test_batch():
	a=mock_lc.MockClient(apikey,host,port,scure)
	a.testname("test_batch")
	a.connect()
	kv={b"cat": b"meow", b"dog": b"woff", b"snake":b"rattle"}
	a.setBatch(kv)
	resp=a.getBatch(kv.keys())
	for i in resp:
		assert kv[i.key]==i.value
	for k in kv.keys():
		v=a.getValue(k)
		assert kv[k]==v
	resp=a.getValueBatch(kv.keys())
	for i in resp.keys():
		assert kv[i]==resp[i]
	for i in kv.keys():
		assert kv[i]==resp[i]
		
def test_double():
	a=mock_lc.MockClient(apikey,host,port,scure)
	a.testname("test_double")
	a.connect()
	kv={}
	for i in range(0,100):
		k="double_{}".format(i).encode('ascii')
		v="trouble_{}".format(i).encode('ascii')
		kv[k]=v
	a.setBatch(kv)
	a.verifiedSet(b"dodge1",b"viper2")
	a.verifiedSet(b"dodge1",b"viper2")
	for k in kv.keys():
		v=a.getValue(k)
		assert kv[k]==v

def test_scan():
	a=mock_lc.MockClient(apikey,host,port,scure)
	a.testname("test_scan")
	a.connect()
	kv={b"CAT1": b"meow", b"CAT2": b"purr"}
	tx=a.setBatch(kv)
	scanback=a.scan(b'',b"CAT",sinceTx=tx.id)
	assert len(scanback)==2
	for i in scanback:
		assert i.key in kv
		assert kv[i.key]==i.value
		assert i.tx==tx.id

def test_history():
	a=mock_lc.MockClient(apikey,host,port,scure)
	a.testname("test_history")
	a.connect()
	a.set(b"gorilla",b"banana")
	a.history(key=b"gorilla")

def test_z():
	a=mock_lc.MockClient(apikey,host,port,scure)
	a.testname("test_z")
	a.connect()
	a.zAdd(b"vanilla",10.0, b"gorilla")
	a.zScan(b"vanilla",None, 1, False)
	ret=a.verifiedZAdd(b"zoo",0.6,b"cobra")
	assert ret.verified==True
	
#def test_tamper():
	#a=mock_lc.MockClient(apikey,host,port,scure)
	#a.reportTamper(0,b'123',b'123',b'123')
	
