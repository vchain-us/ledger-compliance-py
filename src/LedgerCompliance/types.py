from dataclasses import dataclass

@dataclass
class LCState:
	db: str
	txid: int
	txhash: bytes
	
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
    id: int
    key: bytes
    value: bytes
    timestamp: int
    verified: bool
    refkey: bytes
    
@dataclass    
class HealthInfo:
	status: bool
	version: str


# exceptions
class VerificationException(Exception):
	pass

class ErrMaxWidthExceeded(Exception):
	pass

class ErrIllegalArguments(Exception):
	pass

