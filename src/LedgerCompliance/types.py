from dataclasses import dataclass

@dataclass
class LCIndex:
	txid: int
	
@dataclass
class LCItem:
	txid: int
	key: bytes
	value: bytes

@dataclass
class ZItem:
	txid: int
	key: bytes
	value: bytes
	score: float

    
@dataclass
class SafeSetResponse:
	txid: int
	verified: bool
    
@dataclass
class SafeGetResponse:
    txid: int
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

