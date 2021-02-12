from . import mock_lc
import pytest
import grpc

apikey="dwquppzqfqgvvzpfledoldopkxuhiciicupa"
host="172.31.255.10"
port=33080
scure=False

def test_zero():
	a=mock_lc.MockClient(apikey,host,port,scure)
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
	a.connect()
	h=a.health()
	assert h.status
	
def test_get_set():
	a=mock_lc.MockClient(apikey,host,port,scure)
	a.connect()
	a.set(b"gorilla",b"banana")
	resp=a.get(b"gorilla")
	assert resp.value==b"banana"
	
def test_verifiedSetGeT():
	a=mock_lc.MockClient(apikey,host,port,scure)
	a.connect()
	resp=a.verifiedSet(b"dodge",b"viper")
	resp=a.verifiedGet(b"gorilla")
	assert resp.verified

	
#def test_batch():
	#a=mock_lc.MockClient(apikey,host,port,scure)
	#kv={b"cat": b"meow", b"dog": b"woff"}
	#a.setBatch(kv)
	#kk={b"cat", b"dog"}
	#resp=a.getBatch(kk)
	#for i in resp:
		#assert kv[i.key]==i.value

#def test_scan():
	#a=mock_lc.MockClient(apikey,host,port,scure)
	#kv={b"cat1": b"meow", b"cat2": b"purr"}
	#a.setBatch(kv)
	#a.scan(b"cat")

#def test_history():
	#a=mock_lc.MockClient(apikey,host,port,scure)
	#a.set(b"gorilla",b"banana")
	#a.history(key=b"gorilla")

#def test_z():
	#a=mock_lc.MockClient(apikey,host,port,scure)
	#a.zAdd(b"vanilla",10.0, b"gorilla",1)
	#a.zScan(b"vanilla",None, 1, False)
	#ret=a.safeZAdd(b"zoo",0.6,b"cobra",22)
	#assert ret.verified==True
	#ret=a.safeZAdd(b"zoo",0.6,b"cobra",None)
	#assert ret.verified==False
	
#def test_tamper():
	#a=mock_lc.MockClient(apikey,host,port,scure)
	#a.reportTamper(0,b'123',b'123',b'123')
	
