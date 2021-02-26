from dataclasses import dataclass
import pickle, os.path
from .constants import ROOT_CACHE_PATH
_statefile=ROOT_CACHE_PATH

@dataclass
class LCState:
	db: str
	txid: int
	txhash: bytes

# Trivial implemetation, no persistance
class RootService:
	def __init__(self):
		self.__key=None
		self.__db={}
		
	def use(self, key:str):
		self.__key=key
		
	def get(self) -> LCState:
		if self.__key in self.__db:
			return self.__db[self.__key]
		return None
	
	def set(self, state: LCState):
		self.__db[self.__key]=state


class PersistentRootService(RootService):
	def __init__(self, filename:str=None):
		self.__key=None
		if filename!=None:
			self.__filename = filename
		else:
			self.__filename=os.path.join(os.path.expanduser("~"),_statefile)
		self.__db=self._load()


	def get(self) -> LCState:
		if self.__key in self.__db:
			return self.__db[self.__key]
		return None
	
	def set(self, state: LCState):
		self.__db=self._load()
		self.__db[self.__key]=state
		self._save()
		
	def _load(self):
		newdb={}
		try: 
			with open(self.__filename, "rb") as f:
				newdb=pickle.load(f)
		except FileNotFoundError:
			pass
		except Exception as e:
			print("Warning:",e)
		return newdb

	def _save(self):
		try: 
			with open(self.__filename, "wb") as f:
				newdb=pickle.dump(self.__db,f)
		except Exception as e:
			print("Warning:",e)
