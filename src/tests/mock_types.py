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

@dataclass
class MockHealthInfo:
	status: bool
	version: str
