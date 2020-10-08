# This file creates a series of mock services for testing purpose

from dataclasses import dataclass

@dataclass
class MockPayload:
	index: int
	root: bytes
	
@dataclass
class MockSignature:
	signature: bytes
	publicKey: bytes
	
@dataclass
class MockRoot:
	payload: MockPayload
	signature: MockSignature

@dataclass
class SimpleResponse:
	key: bytes
	value: bytes
	index: int

@dataclass	
class MockProof:
	leaf: bytes
	index: int
	root: bytes
	at: int
	inclusionPath: bytes
	consistencyPath: bytes
	
@dataclass	
class MockSafeGetResponse:
	item: SimpleResponse
	proof: MockProof



fakeSetResponse=MockProof(
	leaf=b"\200\312\322&!\305\200:{\031\202\177j\257\027s\300@>X/=\231\304\031wAQ^\001\3551",
	index=30,
	root=b"\024\027\3168\037\364\237B\233j\360\0233\214rX[\030\225\324\260\007\004\344\301\316\342\340#\033\334\317",
	at=30,
	inclusionPath=[
		b"!\276z\376\021g?\301Ux\316Ea\200l1\315\366?\254\200\033\261\274\332 \221\262a\034vr",
		b"\\D\214\016\254eIl\273\'Zh\347\360\322$m\276\260R\371|hQ\002\014\352\300;#\252\245",
		b"\227\341Z\354\206\001\243\023sh\322<\203O\3046l\2167\315\365\326i\365\353p\006\206\270\3523\364",
		b"\237\034e\307[\304\266_Z\251\233/\267\354\311\201& \342\230\271\313&\241\3131-\030\020V\210\251",
		],
	consistencyPath=[
		b"!\276z\376\021g?\301Ux\316Ea\200l1\315\366?\254\200\033\261\274\332 \221\262a\034vr",
		b"\200\312\322&!\305\200:{\031\202\177j\257\027s\300@>X/=\231\304\031wAQ^\001\3551",
		b"\\D\214\016\254eIl\273\'Zh\347\360\322$m\276\260R\371|hQ\002\014\352\300;#\252\245",
		b"\227\341Z\354\206\001\243\023sh\322<\203O\3046l\2167\315\365\326i\365\353p\006\206\270\3523\364",
		b"\237\034e\307[\304\266_Z\251\233/\267\354\311\201& \342\230\271\313&\241\3131-\030\020V\210\251",
		])

fakeGetResponse=MockSafeGetResponse(
	item=SimpleResponse(
		key=b"gorilla",
		value=b"banana",
		index=6,
	),
	proof=MockProof(
		leaf= b"\200\252\210\352\237\021\311\203\251E\027\003\342\353U\335\335\235\354\226\006\305\246f\343\243u\306\316\236\224\013",
		index=6,
		root= b"\024\027\3168\037\364\237B\233j\360\0233\214rX[\030\225\324\260\007\004\344\301\316\342\340#\033\334\317",
		at= 30,
		inclusionPath=[
		b"\246\352\207\021\037\221\333zI\024\363s\2151\037R\035?\017Z\367\306s\345\267\2611V\225\233l\377",
		b"~\366\267\356\356\276S=*\2648\277\314r\305\270\316\217;j\274\355\266\325\002x\034\304\260\375\000\026",
		b"\343g\021\355x\002\376\241\340\026<\206\223\025\262\3077>e\255r\346i\363\237*@\312\377wH\355",
		b"\371^~aE\230\311\327Y\347\376\222\270\341\245I\364\001\254R\354\007\306X\301\356\234\214,\202\240\303",
		b"\324gT\020\017\0252p9\353\207\204\346\354\245\370\200\222\3679\3668\027\"\232\rv\r\253\276\353\365",
		],
		consistencyPath=[]
		)
	)

fakeRoot={
"set": MockPayload(
	index=29,
	root=b"\3225\265\217,Z\002\030Q\343\035\372Wb?X\305<\020\177eXs\256;KMM\311\351M\251"
	),
"get":MockPayload(
	index=30,
	root=b"\024\027\3168\037\364\237B\233j\360\0233\214rX[\030\225\324\260\007\004\344\301\316\342\340#\033\334\317"
	),
}

class MockServer:
	def __init__(self):
		self.mem={}
	def CurrentRoot(self, dummy):
		return MocRoot()
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
	

from LedgerCompliance.client import Client
class MockClient(Client):
	def __init__(self, apikey: str, host: str, port: int):
		Client.__init__(self, apikey, host, port)
		self._Client__stub=MockServer()
	def LoadFakeRoot(self, which):
		self._Client__rs=fakeRoot[which]
