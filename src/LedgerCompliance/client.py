#
import grpc
# from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from LedgerCompliance.schema import lc_pb2_grpc as lc
from LedgerCompliance import header_manipulator_client_interceptor

class Client:
	def __init__(self, apikey: str, host: str, port: int):
		self.apikey=apikey
		self.host=host
		self.port=port
	        self.channel = grpc.insecure_channel("{}:{}".format(self.host,self.port))
		self.__stub = lc.LcServiceStub(self.channel)
		self.__rs = None

	def set_token_header_interceptor(self, apikey):
		self.header_interceptor = \
		header_manipulator_client_interceptor.header_adder_interceptor(
			'lc-api-key', apikey
		)
		try:
			self.intercept_channel = grpc.intercept_channel(
				self.channel, self.header_interceptor)
		except ValueError as e:
			raise Exception("Attempted to connect on termninated client, channel has been shutdown") from e
		return lc.LcServiceStub(self.intercept_channel)
	
	def connect(self):
		self.__stub=set_token_header_interceptor(apikey)

	
	def safeSet():
		pass
	
	def safeGet():
		pass


