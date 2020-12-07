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
	
	def SetBatch(self, request):
		for r in request.KVs:
			self.mem[r.key]=r.value
		return SimpleResponse(b'', 0, len(self.mem))
	
	def GetBatch(self, request):
		ret=[]
		for r in request.keys:
			sr=SimpleResponse(key=r.key, value=self.mem[r.key], index=len(self.mem))
			ret.append(sr)
		return MockList(items=ret)
	def Scan(self, request):
		ret=[]
		for k in self.mem.keys():
			if k.startswith(request.prefix):
				sr=SimpleResponse(key=k, value=self.mem[k], index=len(self.mem))
				ret.append(sr)
		return MockList(items=ret)
	def History(self, request):
		sr=SimpleResponse(key=request.key, value=self.mem[request.key], index=len(self.mem))
		ret=[sr,]
		return MockList(items=ret)
		
	def ZAdd(self, request):
		self.mem[request.set]=b"%f"%request.score.score
		return SimpleResponse(request.key, 0, len(self.mem))
	
	def SafeZAdd(self, request):
		self.mem[request.zopts.set]=b"%f"%request.zopts.score.score
		return fakeSafeZSetResponse

	def ZScan(self, request):
		sr=SimpleResponse(key=request.set, value=self.mem[request.set], index=len(self.mem))
		ret=[sr,]
		return MockList(items=ret)

from LedgerCompliance.client import Client
class MockClient(Client):
	def __init__(self, apikey: str, host: str, port: int, secure:bool=True):
		Client.__init__(self, apikey, host, port, secure)
		self._Client__stub=MockServer()
	def LoadFakeRoot(self, which):
		self._Client__rs=fakeRoot[which]
		
	def fake_set_interceptor(self, apikey):
		return MockServer()
	def InterceptInterceptor(self):
		self.set_interceptor=self.fake_set_interceptor
