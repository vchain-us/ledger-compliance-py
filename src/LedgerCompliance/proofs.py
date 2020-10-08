import hashlib
import struct
from copy import deepcopy

LEAF_PREFIX = 0
NODE_PREFIX = 1


def digest(index: int, key: bytes, value: bytes) -> bytes:
	c = bytearray()
	c.append(LEAF_PREFIX)
	c.extend(struct.pack('>Q', index))
	c.extend(struct.pack('>Q', len(key)))
	c.extend(key)
	c.extend(value)
	return hashlib.sha256(c).digest()

def path_verify(path:list, at:int, i:int, root:bytes, leaf:bytes) -> bool:
	if i > at or (at > 0 and len(path) == 0):
		return False
	h = leaf
	for v in path:
		c = bytearray()
		c.append(NODE_PREFIX)
		v = bytes(v)
		if i%2 == 0 and i != at:
			c.extend(h)
			c.extend(v)
		else:
			c.extend(v)
			c.extend(h)
		h = hashlib.sha256(c).digest()
		i = i // 2
		at = at // 2
	return at == i and h == root
def isPowerOfTwo(x: int) -> bool:
    return (x != 0) and ((x & (x-1)) == 0)


def verify_path(path: list, second: int, first: int, secondHash: bytes, firstHash: bytes) -> bool:
	l = len(path)
	if first == second and firstHash == secondHash and l == 0:
		return True
	if not(first < second) or l == 0:
		return False
	pp = path
	if isPowerOfTwo(first + 1):
		pp = [firstHash]
		pp.extend(path)
	fn = first
	sn = second
	while (fn % 2) == 1:
		fn >>= 1
		sn >>= 1
	fr = pp[0]
	sr = pp[0]
	isFirst = True
	for c in pp:
		if isFirst:
			isFirst = False
			continue
		if sn == 0:
			return False
		if (fn % 2) == 1 or fn == sn:
			tmp = bytearray()
			tmp.append(NODE_PREFIX)
			tmp.extend(c)
			tmp.extend(fr)
			fr = hashlib.sha256(tmp).digest()
			tmp = bytearray()
			tmp.append(NODE_PREFIX)
			tmp.extend(c)
			tmp.extend(sr)
			sr = hashlib.sha256(tmp).digest()
			while (fn%2) == 0 and fn != 0:
				fn >>= 1
				sn >>= 1
		else:
			tmp = bytearray()
			tmp.append(NODE_PREFIX)
			tmp.extend(sr)
			tmp.extend(c)
			sr = hashlib.sha256(tmp).digest()
		fn >>= 1
		sn >>= 1
	return fr == firstHash and sr == secondHash and sn == 0

def verify(proof, leaf, prevRoot) -> bool:
	if bytes(proof.leaf) != leaf:
		return False

	path = deepcopy(proof.inclusionPath)

	verifiedInclusion = path_verify(
		path,
		proof.at,
		proof.index,
		deepcopy(proof.root),
		deepcopy(proof.leaf)
	)

	if not verifiedInclusion:
		return False

	if prevRoot.index == 0 or len(prevRoot.root) == 0:
		return True

	path = deepcopy(proof.consistencyPath)

	return verify_path(path, proof.at, prevRoot.index, proof.root, prevRoot.root)
