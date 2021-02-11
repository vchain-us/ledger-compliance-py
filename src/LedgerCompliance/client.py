#
import grpc
from google.protobuf import empty_pb2 as empty_request
from LedgerCompliance.schema import lc_pb2_grpc as lc
from LedgerCompliance.schema import schema_pb2_grpc as immudb
from LedgerCompliance.schema.schema_pb2_grpc import schema__pb2 as schema_pb2
from LedgerCompliance.schema.lc_pb2_grpc import lc__pb2 as lc_pb2

from LedgerCompliance import header_manipulator_client_interceptor as interceptor
from . import types, proofs, utils, constants
import time

class Client:
	def __init__(self, apikey: str, host: str, port: int, secure:bool=True):
		self.apikey=apikey
		self.host=host
		self.port=port
		if secure:
			self.credentials=grpc.ssl_channel_credentials()
			self.channel = grpc.secure_channel(
				"{}:{}".format(self.host,self.port),self.credentials)
		else:
			self.channel = grpc.insecure_channel(
				"{}:{}".format(self.host,self.port))
		self.__stub = lc.LcServiceStub(self.channel)
		self.__rs = None
		
	def set_credentials(self, root_certificates=None, private_key=None, certificate_chain=None):
		self.credentials=grpc.ssl_channel_credentials(
			root_certificates, private_key, certificate_chain)
		self.channel = grpc.secure_channel(
			"{}:{}".format(self.host,self.port),self.credentials)
		self.__stub = lc.LcServiceStub(self.channel)
		self.__rs = None

	def set_interceptor(self, apikey):
		""" Set up an interceptor so all grpc calls will have the apikey
		added on the header, in order to authenticate.
		"""
		self.header_interceptor = \
		interceptor.header_adder_interceptor(
			'lc-api-key', apikey
		)
		try:
			self.intercept_channel = grpc.intercept_channel(
				self.channel, self.header_interceptor)
		except ValueError as e:
			raise Exception("Attempted to connect on termninated client, "
				"channel has been shutdown") from e
		return lc.LcServiceStub(self.intercept_channel)
	
	def connect(self):
		self.__stub=self.set_interceptor(self.apikey)
		return self.currentState()
	
	def currentState(self):
		resp=self.__stub.CurrentState(empty_request.Empty())
		self.__rs=types.LCState(
			db=resp.db,
			txid=resp.txId,
			txhash=resp.txHash
		)
		return self.__rs
		

	def set(self, key: bytes, value: bytes):
		now=int(time.time())
		content = schema_pb2.Content(timestamp=now, payload=value)
		request = schema_pb2.KeyValue(key=key, value=content.SerializeToString())
		ret=self.__stub.Set(request)
		return types.LCIndex(index=ret.index)
	
	def get(self, key:bytes):
		request = schema_pb2.Key(key=key)
		ret=self.__stub.Get(request)
		content=schema_pb2.Content()
		content.ParseFromString(ret.value)
		return types.LCItem(key=ret.key, value=content.payload, index=ret.index, timestamp=content.timestamp)
	
	def _mkProof(self, msg):
		proof=types.Proof(
			leaf=msg.leaf,
			index=msg.index,
			root=msg.root,
			at=msg.at,
			inclusionPath=msg.inclusionPath,
			consistencyPath=msg.consistencyPath,
			)
		return proof
	
	def verifiedSet(self, key: bytes, value: bytes):
		# print(base64.b64encode(state.SerializeToString()))
		kv = schema_pb2.KeyValue(key=key, value=value)
		rawRequest = schema_pb2.VerifiableSetRequest(
			setRequest = schema_pb2.SetRequest(KVs=[kv]),
			proveSinceTx= self.__rs.txid,
		)
		verifiableTx = self.__stub.VerifiableSet(rawRequest)
		# print(base64.b64encode(verifiableTx.SerializeToString()))
		tx=proofs.TxFrom(verifiableTx.tx)
		inclusionProof=tx.Proof(constants.SET_KEY_PREFIX+key)
		ekv=proofs.EncodeKV(key, value)
		verifies=proofs.VerifyInclusion(inclusionProof, ekv.Digest(), tx.eh())
		if not verifies:
			raise types.VerificationException
		if tx.eh() != proofs.DigestFrom(verifiableTx.dualProof.targetTxMetadata.eH):
			raise types.VerificationException
		if self.__rs.txid == 0:
			sourceID = tx.ID
			sourceAlh = tx.Alh
		else:
			sourceID = self.__rs.txid
			sourceAlh = proofs.DigestFrom(self.__rs.txhash)
		targetID = tx.ID
		targetAlh = tx.Alh

		verifies = proofs.VerifyDualProof( proofs.DualProofFrom(verifiableTx.dualProof), sourceID, targetID, sourceAlh, targetAlh, )
		if not verifies:
			raise types.VerificationException
		self.__rs=types.LCState(
			db=self.__rs.db,
			txid=targetID,
			txhash=targetAlh
		)
		return types.SafeSetResponse(
			index=targetID,
			verified=verifies,
			proof=targetAlh,
		)
	
	def verifiedGet(self, requestkey: bytes, atTx:int=None):
		if atTx==None:
			req = schema_pb2.VerifiableGetRequest(
			keyRequest= schema_pb2.KeyRequest(key=requestkey),
			proveSinceTx= self.__rs.txid
			)
		else:
			req = schema_pb2.VerifiableGetRequest(
			keyRequest= schema_pb2.KeyRequest(key=requestkey, atTx=atTx),
			proveSinceTx= self.__rs.txid
			)
		ventry=self.__stub.VerifiableGet(req)
		inclusionProof = proofs.InclusionProofFrom(ventry.inclusionProof)
		dualProof = proofs.DualProofFrom(ventry.verifiableTx.dualProof)
		
		if ventry.entry.referencedBy==None or ventry.entry.referencedBy.key==b'':
			vTx=ventry.entry.tx
			kv=proofs.EncodeKV(requestkey, ventry.entry.value)
		else:
			vTx = ventry.entry.referencedBy.tx
			kv=proofs.EncodeReference(ventry.entry.referencedBy.key, ventry.entry.key, ventry.entry.referencedBy.atTx) 
			
		if self.__rs.txid <= vTx:
			eh=proofs.DigestFrom(ventry.verifiableTx.dualProof.targetTxMetadata.eH)
			sourceid=self.__rs.txid
			sourcealh=proofs.DigestFrom(self.__rs.txhash)
			targetid=vTx
			targetalh=dualProof.targetTxMetadata.alh()
		else:
			eh=proofs.DigestFrom(ventry.verifiableTx.dualProof.sourceTxMetadata.eH)
			sourceid=vTx
			sourcealh=dualProof.sourceTxMetadata.alh()
			targetid=self.__rs.txid
			targetalh=proofs.DigestFrom(self.__rs.txhash)
			
		verifies = proofs.VerifyInclusion(inclusionProof,kv.Digest(),eh)
		if not verifies:
			raise VerificationException
		verifies=proofs.VerifyDualProof( dualProof, sourceid, targetid, sourcealh, targetalh)
		if not verifies:
			raise VerificationException
		self.__rs=types.LCState( db=self.__rs.db, txid=targetid, txhash=targetalh )
		if ventry.entry.referencedBy!=None and ventry.entry.referencedBy.key!=b'':
			refkey=ventry.entry.referencedBy.key
		else:
			refkey=None
		return types.SafeGetResponse(
			id=vTx,
			key=ventry.entry.key,
			value=ventry.entry.value,
			timestamp=ventry.verifiableTx.tx.metadata.ts,
			verified=verifies,
			refkey=refkey
			)
	def health(self):
		resp=self.__stub.Health(empty_request.Empty())
		return types.HealthInfo(status=resp.status, version=resp.version)
	
	def setBatch(self, kv: dict):
		_KVs = []
		now=int(time.time())
		for i in kv.keys():
			content=schema_pb2.Content(timestamp=now, payload=kv[i])
			_KVs.append(schema_pb2.KeyValue( key=i, value=content.SerializeToString()) )
		request = schema_pb2.KVList(KVs=_KVs)
		ret=self.__stub.SetBatch(request)
		return types.LCIndex(index=ret.index)
	
	def _parseItemList(self,items):
		values=[]
		for r in items:
			content=schema_pb2.Content()
			content.ParseFromString(r.value)
			values.append(types.LCItem(
				key=r.key, 
				value=content.payload, 
				index=r.index, 
				timestamp=content.timestamp
			))
		return values

	def getBatch(self, keys: list):
		klist = [schema_pb2.Key(key=k) for k in keys]
		request = schema_pb2.KeyList(keys=klist)
		ret=self.__stub.GetBatch(request)
		return self._parseItemList(ret.items)
	
	def scan(self, prefix:bytes, offset:bytes=b'', limit:int=0, reverse:bool=False, deep:bool=False):
		request = schema_pb2.ScanOptions(
			prefix=prefix,
			offset=offset,
			limit=limit,
			reverse=reverse,
			deep=deep
			)
		ret=self.__stub.Scan(request)
		return self._parseItemList(ret.items)
	
	def history(self, key: bytes):
		request = schema_pb2.Key(key=key)
		ret=self.__stub.History(request)
		return self._parseItemList(ret.items)
	
	def zAdd(self, zset:bytes, score:float, key:bytes, index:int):
		scor=schema_pb2.Score(score=score)
		idx=schema_pb2.Index(index=index)
		request = schema_pb2.ZAddOptions(set=zset, score=scor, key=key, index=idx)
		ret= self.__stub.ZAdd(request)
		return types.LCIndex(index=ret.index)
	
	def safeZAdd(self, zset:bytes, score:float, key:bytes, index:int=None):
		if index!=None:
			idx=schema_pb2.Index(index=index)
		else:
			idx=None
		scor=schema_pb2.Score(score=score)
		opt = schema_pb2.ZAddOptions(set=zset, score=scor, key=key, index=idx)
		rootindex=schema_pb2.Index(index=self.__rs.index)
		request = schema_pb2.SafeZAddOptions(zopts=opt, rootIndex=rootindex)
		msg= self.__stub.SafeZAdd(request) # msg type is "Proof"
		#print("MSG:",msg,"/MSG")
		# message verification
		key2=utils.build_set_key(key, zset, score, idx)
		value=utils.wrap_zindex_ref(key, idx)
		digest = proofs.digest(msg.index, key2, value)
		verified = proofs.verify(msg, digest, self.__rs)
		
		if verified:
			# Update root
			self.__rs=schema_pb2.RootIndex(index=msg.at, root=msg.root)
		proof=self._mkProof(msg)
		return types.SafeSetResponse(
			index=msg.index,
			proof=proof,
			verified=verified
		)
	
	def zScan(self, zset: bytes, offset: bytes, limit: int, reverse:bool):
		request=schema_pb2.ZScanOptions(set=zset, offset=offset, limit=limit, reverse=reverse)
		ret=self.__stub.ZScan(request)
		return self._parseItemList(ret.items)
	
	def reportTamper(self, index:int, key:bytes, signature:bytes=None, publickey:bytes=None):
		report=lc_pb2.TamperReport(index=index, key=key, root=self.__rs.root)
		signature=schema_pb2.Signature(signature=signature, publicKey=publickey)
		request=lc_pb2.ReportOptions(payload=report, signature=signature)
		self.__stub.ReportTamper(request)
	

