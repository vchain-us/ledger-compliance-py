from . import mock_lc
import pytest
import grpc
def test_zero():
	apikey="justatest"
	host="127.0.0.1"
	port=3324
	a=mock_lc.MockClient(apikey,host,port)
	a.currentRoot()
	
def test_connect():
	apikey="justatest"
	host="127.0.0.1"
	port=3324
	a=mock_lc.MockClient(apikey,host,port,secure=False)
	a=mock_lc.MockClient(apikey,host,port,secure=True)
	a.set_credentials()
	try:
		a.connect()
	except grpc._channel._InactiveRpcError as e:
		pass
	a.InterceptInterceptor()
	a.connect()
	
def test_health():
	apikey="justatest"
	host="127.0.0.1"
	port=3324
	a=mock_lc.MockClient(apikey,host,port)
	h=a.health()
	assert h.status
	
def test_get_set():
	apikey="justatest"
	host="127.0.0.1"
	port=3324
	a=mock_lc.MockClient(apikey,host,port)
	a.set(b"gorilla",b"banana")
	resp=a.get(b"gorilla")
	assert resp.value==b"banana"
	
def test_safeSet():
	apikey="justatest"
	host="127.0.0.1"
	port=3324
	a=mock_lc.MockClient(apikey,host,port)
	a.LoadFakeRoot('set')
	resp=a.safeSet(b"dodge",b"viper")
	assert resp.verified

def test_safeGet():
	apikey="justatest"
	host="127.0.0.1"
	port=3324
	a=mock_lc.MockClient(apikey,host,port)
	a.LoadFakeRoot('get')
	resp=a.safeGet(b"gorilla")
	assert resp.verified

def test_tamperGet():
	apikey="justatest"
	host="127.0.0.1"
	port=3324
	a=mock_lc.MockClient(apikey,host,port)
	a.LoadFakeRoot('set')
	resp=a.safeGet(b"gorilla")
	assert not resp.verified
	
def test_batch():
	apikey="justatest"
	host="127.0.0.1"
	port=3324
	a=mock_lc.MockClient(apikey,host,port)
	kv={b"cat": b"meow", b"dog": b"woff"}
	a.setBatch(kv)
	kk={b"cat", b"dog"}
	resp=a.getBatch(kk)
	for i in resp:
		assert kv[i.key]==i.value

def test_scan():
	apikey="justatest"
	host="127.0.0.1"
	port=3324
	a=mock_lc.MockClient(apikey,host,port)
	kv={b"cat1": b"meow", b"cat2": b"purr"}
	a.setBatch(kv)
	a.scan(b"cat")

def test_history():
	apikey="justatest"
	host="127.0.0.1"
	port=3324
	a=mock_lc.MockClient(apikey,host,port)
	a.set(b"gorilla",b"banana")
	a.history(key=b"gorilla")

def test_z():
	apikey="justatest"
	host="127.0.0.1"
	port=3324
	a=mock_lc.MockClient(apikey,host,port)
	a.LoadFakeRoot('set')
	a.zAdd(b"vanilla",10.0, b"gorilla",1)
	a.zScan(b"vanilla",None, 1, False)
	a.LoadFakeRoot('safezadd')
	ret=a.safeZAdd(b"zoo",0.6,b"cobra",22)
	assert ret.verified==True
	ret=a.safeZAdd(b"zoo",0.6,b"cobra",None)
	assert ret.verified==False
	
	
