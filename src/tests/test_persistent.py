from . import mock_lc
import pytest
import grpc
import tempfile,os
from LedgerCompliance import stateservice

apikey="bzlmqybrgezwarnnkkrypkmthkrvmsolranb"
host="172.31.255.10"
port=33080
scure=False

@pytest.fixture(scope="module")
def rootfile():
	with tempfile.NamedTemporaryFile(delete=False) as f:
		yield f.name
	os.unlink(f.name)

def test_zero():
	a=mock_lc.MockClient(apikey,host,port,scure)
	a.testname("test_zero")
	rs=stateservice.PersistentRootService(rootfile)
	a.connect(rs)
	a.currentState()

def test_verifiedSetGet():
	a=mock_lc.MockClient(apikey,host,port,scure)
	a.testname("test_verifiedSetGet")
	rs=stateservice.PersistentRootService(rootfile)
	a.connect(rs)
	resp=a.verifiedSet(b"dodge",b"viper")
	resp=a.verifiedGet(b"dodge",resp.txid)
	resp=a.verifiedGet(b"gorilla")
	assert resp.verified


