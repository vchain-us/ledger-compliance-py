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
	a=mock_lc.MockClient(apikey,host,port)
	try:
		a.connect()
	except grpc._channel._InactiveRpcError as e:
		pass
	
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
