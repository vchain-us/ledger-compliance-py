# This file creates a series of mock services for testing purpose

from .mock_types import *
from .fake import *

class MockServer:
	def __init__(self):
		self.mem={}
	def CurrentRoot(self, dummy):
		t1=MockPayload(0,b'')
		t2=MockSignature(b'',b'')
		return MockRoot(t1,t2)
	def Set(self, request):
		self.mem[request.key]=request.value
		return SimpleResponse(request.key, request.value, len(self.mem))
	def Get(self, request):
		value=None
		if request.key in self.mem:
			value=self.mem[request.key]
		return SimpleResponse(request.key, value, len(self.mem))
	def SafeSet(self, request):
		return fakeSetResponse
		
	def SafeGet(self, request):
		return fakeGetResponse
	
	def Health(self, request):
		return MockHealthInfo(True, "(s)Mocking!")
	

from LedgerCompliance.client import Client
class MockClient(Client):
	def __init__(self, apikey: str, host: str, port: int):
		Client.__init__(self, apikey, host, port)
		self._Client__stub=MockServer()
	def LoadFakeRoot(self, which):
		self._Client__rs=fakeRoot[which]
