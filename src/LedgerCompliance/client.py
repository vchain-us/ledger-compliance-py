#
import grpc
from google.protobuf import empty_pb2 as empty_request
from LedgerCompliance.schema import lc_pb2_grpc as lc
from LedgerCompliance.schema import schema_pb2_grpc as immudb
from LedgerCompliance.schema.schema_pb2_grpc import schema__pb2 as schema_pb2
from LedgerCompliance.schema.lc_pb2_grpc import lc__pb2 as lc_pb2

from LedgerCompliance import header_manipulator_client_interceptor as interceptor
from . import types, proofs, utils, constants, stateservice
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
	
	def connect(self, rs=None):
		self.__stub=self.set_interceptor(self.apikey)
		if rs!=None:
			self.__rs=rs
		else:
			self.__rs=stateservice.RootService()
		self.__rs.use(self.apikey)
		return self.currentState()
	
	def currentState(self):
		state=self.__rs.get()
		if state==None:
			resp=self.__stub.CurrentState(empty_request.Empty())
			state=stateservice.LCState(
				db=resp.db,
				txid=resp.txId,
				txhash=resp.txHash
				)
			self.__rs.set(state)
		return state
		
	def set(self, key: bytes, value: bytes):
		request=schema_pb2.SetRequest(
			KVs=[schema_pb2.KeyValue(key=key, value=value)]
		)
		ret = self.__stub.Set(request)
		return types.LCIndex(txid=ret.id)
	
	def get(self, key:bytes) -> types.LCIndex:
		request = schema_pb2.Key(key=key)
		ret=self.__stub.Get(request)
		return types.LCItem(key=ret.key, value=ret.value, txid=ret.tx)
	
	def getValue(self, key:bytes) -> bytes:
		request = schema_pb2.Key(key=key)
		ret=self.__stub.Get(request)
		return ret.value

	def verifiedSet(self, key: bytes, value: bytes):
		state=self.currentState()
		# print(base64.b64encode(state.SerializeToString()))
		kv = schema_pb2.KeyValue(key=key, value=value)
		rawRequest = schema_pb2.VerifiableSetRequest(
			setRequest = schema_pb2.SetRequest(KVs=[kv]),
			proveSinceTx= state.txid,
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
		if state.txid == 0:
			sourceID = tx.ID
			sourceAlh = tx.Alh
		else:
			sourceID = state.txid
			sourceAlh = proofs.DigestFrom(state.txhash)
		targetID = tx.ID
		targetAlh = tx.Alh

		verifies = proofs.VerifyDualProof( proofs.DualProofFrom(verifiableTx.dualProof), sourceID, targetID, sourceAlh, targetAlh, )
		if not verifies:
			raise types.VerificationException
		state.txid=targetID
		state.txhash=targetAlh
		self.__rs.set(state)
		return types.SafeSetResponse(
			txid=targetID,
			verified=verifies,
		)
	
	def verifiedGet(self, requestkey: bytes, atTx:int=None):
		state=self.currentState()
		if atTx==None:
			req = schema_pb2.VerifiableGetRequest(
			keyRequest= schema_pb2.KeyRequest(key=requestkey),
			proveSinceTx= state.txid
			)
		else:
			req = schema_pb2.VerifiableGetRequest(
			keyRequest= schema_pb2.KeyRequest(key=requestkey, atTx=atTx),
			proveSinceTx= state.txid
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
			
		if state.txid <= vTx:
			eh=proofs.DigestFrom(ventry.verifiableTx.dualProof.targetTxMetadata.eH)
			sourceid=state.txid
			sourcealh=proofs.DigestFrom(state.txhash)
			targetid=vTx
			targetalh=dualProof.targetTxMetadata.alh()
		else:
			eh=proofs.DigestFrom(ventry.verifiableTx.dualProof.sourceTxMetadata.eH)
			sourceid=vTx
			sourcealh=dualProof.sourceTxMetadata.alh()
			targetid=state.txid
			targetalh=proofs.DigestFrom(state.txhash)
			
		verifies = proofs.VerifyInclusion(inclusionProof,kv.Digest(),eh)
		if not verifies:
			raise VerificationException
		verifies=proofs.VerifyDualProof( dualProof, sourceid, targetid, sourcealh, targetalh)
		if not verifies:
			raise VerificationException
		state.txid=targetid
		state.txhash=targetalh
		self.__rs.set(state)
		if ventry.entry.referencedBy!=None and ventry.entry.referencedBy.key!=b'':
			refkey=ventry.entry.referencedBy.key
		else:
			refkey=None
		return types.SafeGetResponse(
			txid=vTx,
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
		ops=[]
		for (key,value) in kv.items():
			xreq=schema_pb2.Op(
					kv=schema_pb2.KeyValue(key=key, value=value)
					)
			ops.append(xreq)
		request=schema_pb2.ExecAllRequest(
			Operations=ops
		)		
		ret=self.__stub.ExecAll(request)
		return types.LCIndex(txid=ret.id)
	
	def getBatch(self, keys: list):
		request = schema_pb2.KeyListRequest(keys=keys)
		ret=self.__stub.GetAll(request)
		return [types.LCItem(key=t.key, value=t.value, txid=t.tx) for t in ret.entries]
	
	def getValueBatch(self, keys: list):
		request = schema_pb2.KeyListRequest(keys=keys)
		ret=self.__stub.GetAll(request)
		return {t.key:t.value for t in ret.entries}
	
	def scan(self, seekKey:bytes, prefix:bytes, desc:bool=False, limit:int=10, sinceTx:int=None, noWait:bool=False):
		request = schema_pb2.ScanRequest(
			seekKey = seekKey ,
			prefix = prefix, 
			desc = desc, 
			limit = limit, 
			sinceTx = sinceTx,
			noWait = noWait
			)
		ret=self.__stub.Scan(request)
		return [types.LCItem(key=t.key, value=t.value, txid=t.tx) for t in ret.entries]
	
	def history(self, key: bytes, offset:int=0, limit:int=10, desc:bool=False, sinceTx:int=0):
		request = schema_pb2.HistoryRequest(
			key=key, offset=offset, limit=limit, desc=desc, sinceTx=sinceTx)
		ret=self.__stub.History(request)
		return [types.LCItem(key=t.key, value=t.value, txid=t.tx) for t in ret.entries]
	
	def zAdd(self, zset:bytes, score:float, key:bytes, atTx:int=0):
		request = schema_pb2.ZAddRequest(set=zset, score=score, key=key, atTx=atTx,
				   boundRef=atTx>0)
		ret= self.__stub.ZAdd(request)
		return types.LCIndex(txid=ret.id)
	
	def verifiedZAdd(self, zset:bytes, score:float, key:bytes, atTx:int=0):
		state=self.currentState()
		request=schema_pb2.VerifiableZAddRequest(
			zAddRequest=schema_pb2.ZAddRequest(
			set=      zset,
			score=    score,
			key=      key,
			atTx=     atTx,
			),
			proveSinceTx=state.txid
			)
		vtx = self.__stub.VerifiableZAdd(request)
		if vtx.tx.metadata.nentries!=1:
			raise VerificationException
		tx = proofs.TxFrom(vtx.tx)
		ekv = proofs.EncodeZAdd(zset, score, key, atTx)
		inclusionProof=tx.Proof(ekv.key)
		verifies = proofs.VerifyInclusion(inclusionProof, ekv.Digest(), tx.eh())
		if not verifies:
			raise VerificationException
		if tx.eh() != proofs.DigestFrom(vtx.dualProof.targetTxMetadata.eH):
			raise VerificationException
		if state.txid == 0:
			sourceID = tx.ID
			sourceAlh = tx.Alh
		else:
			sourceID = state.txid
			sourceAlh = proofs.DigestFrom(state.txhash)
		targetID = tx.ID
		targetAlh = tx.Alh
		verifies = proofs.VerifyDualProof(
			proofs.DualProofFrom(vtx.dualProof),
			sourceID,
			targetID,
			sourceAlh,
			targetAlh,
		)
		if not verifies:
			raise VerificationException

		state.txid=targetID
		state.txhash=targetAlh
		self.__rs.set(state)
		return types.SafeSetResponse(
			txid=targetID,
			verified=verifies,
		)
	
	def zScan(self, zset:bytes, seekKey:bytes, seekScore:float, 
			inclusiveSeek:bool=False, seekAtTx:int=0, limit:int=10, desc:bool=False,
			minScore:float=None, maxScore:float=None, sinceTx:int=0, noWait:bool=False):
		
		request=schema_pb2.ZScanRequest(set=zset, seekKey=seekKey, seekScore=seekScore,
				  seekAtTx=seekAtTx, inclusiveSeek=inclusiveSeek, limit=limit, desc=desc,
				  minScore=schema_pb2.Score(score=minScore),
				  maxScore=schema_pb2.Score(score=maxScore), 
				  sinceTx=sinceTx, noWait=noWait)
				  
		ret=self.__stub.ZScan(request)
		print(ret)
		return [types.ZItem(key=t.entry.key, value=t.entry.value, txid=t.entry.tx, score=t.score) for t in ret.entries]
	
	def reportTamper(self, index:int, key:bytes, signature:bytes=None, publickey:bytes=None):
		state=self.currentState()
		report=lc_pb2.TamperReport(index=index, key=key, root=state.root)
		signature=schema_pb2.Signature(signature=signature, publicKey=publickey)
		request=lc_pb2.ReportOptions(payload=report, signature=signature)
		self.__stub.ReportTamper(request)
	

