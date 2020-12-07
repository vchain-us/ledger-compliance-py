import LedgerCompliance.utils as utils
from dataclasses import dataclass

@dataclass
class Index:
	index: int

def test_wrap():
	idx=Index(index=12)
	a1=utils.wrap_zindex_ref(b"gorilla",idx)
	k1,v1=utils.unwrap_zindex_ref(a1)
	assert(k1==b"gorilla")
	assert(v1==12)

def test_nullwrap():
	idx=Index(index=None)
	a1=utils.wrap_zindex_ref(b"gorilla",idx)
	k1,v1=utils.unwrap_zindex_ref(a1)
	assert(k1==b"gorilla")
	assert(v1==None)
