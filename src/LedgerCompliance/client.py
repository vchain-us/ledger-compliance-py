#
import grpc
from google.protobuf import empty_pb2 as empty_request
from LedgerCompliance.schema import lc_pb2_grpc as lc
from LedgerCompliance.schema import schema_pb2_grpc as immudb
from LedgerCompliance.schema.schema_pb2_grpc import schema__pb2 as schema_pb2

from LedgerCompliance import header_manipulator_client_interceptor as interceptor
from . import types, proofs

class Client:
	def __init__(self, apikey: str, host: str, port: int):
		self.apikey=apikey
		self.host=host
		self.port=port
		self.channel = grpc.insecure_channel("{}:{}".format(self.host,self.port))
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
		resp=self.__stub.CurrentRoot(empty_request.Empty())
		self.__rs=resp.payload
		return types.LCRoot(
			index=resp.payload.index,
			root=resp.payload.root,
			signature=resp.signature.signature, 
			publicKey=resp.signature.publicKey
		)
	
	def currentRoot(self):
		resp=self.__stub.CurrentRoot(empty_request.Empty())
		self.__rs=resp.payload
		return types.LCRoot(
			index=resp.payload.index,
			root=resp.payload.root,
			signature=resp.signature.signature, 
			publicKey=resp.signature.publicKey
		)
		

	def set(self, key: bytes, value: bytes):
		request = schema_pb2.KeyValue(key=key, value=value)
		ret=self.__stub.Set(request)
		return types.LCIndex(index=ret.index)
	
	def get(self, key:bytes):
		request = schema_pb2.Key(key=key)
		ret=self.__stub.Get(request)
		return types.LCItem(key=ret.key, value=ret.value, index=ret.index)
	
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
	
	def safeSet(self, key: bytes, value: bytes):
		kv = schema_pb2.KeyValue(key=key, value=value)
		index=schema_pb2.Index(index=self.__rs.index)
		request=schema_pb2.SafeSetOptions(kv=kv, rootIndex=index)
		msg=self.__stub.SafeSet(request) # msg type is "Proof"
		
		# message verification
		digest = proofs.digest(msg.index, key, value)
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
	
	def safeGet(self, key: bytes):
		index=schema_pb2.Index(index=self.__rs.index)
		request=schema_pb2.SafeGetOptions(key=key, rootIndex=index)
		msg = self.__stub.SafeGet(request)
		
		# message verification
		digest = proofs.digest(msg.item.index, key, msg.item.value)
		verified = proofs.verify(msg.proof, digest, self.__rs)

		if verified:
			# Update root
			self.__rs=schema_pb2.RootIndex(index=msg.proof.at, root=msg.proof.root)
		proof=self._mkProof(msg.proof)
		return types.SafeGetResponse(
			index=msg.item.index,
			key=msg.item.key,
			value=msg.item.value,
			proof=proof,
			verified=verified
			)
	def health(self):
		resp=self.__stub.Health(empty_request.Empty())
		return types.HealthInfo(status=resp.status, version=resp.version)

