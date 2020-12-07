import struct

_SetSeparator=b"_~|IMMU|~_"

def wrap_zindex_ref(key: bytes, index) -> bytes:
	fmt=">{}sQB".format(len(key))
	if index!=None and index.index!=None:
		ret=struct.pack(fmt,key,index.index,1)
	else:
		ret=struct.pack(fmt,key,0,0)
	return ret

def unwrap_zindex_ref(value:bytes):
	l=len(value)
	fmt=">{}sQB".format(l-8-1)
	key, index, flag = struct.unpack(fmt,value)
	if flag==0:
		index=None
	return (key,index)

def build_set_key(key: bytes, zset: bytes, score: float, index) -> bytes:
	ret=_SetSeparator + zset + _SetSeparator + float64_2_bytes(score) + key
	ret=wrap_zindex_ref(ret,index)
	return ret

def float64_2_bytes(f:float)->bytes:
	return struct.pack(">d",f)
	
