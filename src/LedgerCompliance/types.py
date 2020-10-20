from dataclasses import dataclass

@dataclass
class LCRoot:
	index: int
	root: bytes
	signature: bytes
	publicKey: bytes
	
@dataclass
class LCIndex:
	index: int
	
@dataclass
class LCItem:
	key: bytes
	value: bytes
	index: int
	timestamp: int

@dataclass
class Proof:
	index: bytes
	leaf: bytes 
	root: bytes
	at: int
	inclusionPath: bytes
	consistencyPath: bytes
    
@dataclass
class SafeSetResponse:
	index: int
	verified: bool
	proof: Proof
    
@dataclass
class SafeGetResponse:
	index: int
	key: bytes
	value: bytes
	timestamp: int
	verified: bool
	proof: Proof
    
@dataclass    
class HealthInfo:
	status: bool
	version: str
