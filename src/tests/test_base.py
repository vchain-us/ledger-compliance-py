from . import mock_lc
import pytest

def test_zero():
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
