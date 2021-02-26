from dataclasses import dataclass

@dataclass
class LCState:
	db: str
	txid: int
	txhash: bytes

# Trivial implemetation, no persistance
class RootService:
	def __init__(self, key:str):
		self.__key=key
		self.__db={}
		
	def get(self) -> LCState:
		if self.__key in self.__db:
			return self.__db[self.__key]
		return None
	
	def set(self, state: LCState):
		self.__db[self.__key]=state
