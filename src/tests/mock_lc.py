# This file creates a series of mock services for testing purpose

import hashlib,base64,pickle
from google.protobuf import message
from LedgerCompliance.schema.schema_pb2_grpc import schema__pb2 as schema_pb2

MODE_REC=0
MODE_PLAY=1


MODE=MODE_PLAY

class MockServer(object):
    def __init__(self, mode, realserver):
        self.mode=mode
        self.realserver=realserver
        self.read_state()
        self.testname=None
        
    def read_state(self):
        self.db={}
        try:
            with open("./.mockserver.state","rb") as f:
                self.db=pickle.load(f)
        except:
            print("Initializing emtpy db")
    def save_state(self):
        with open("./.mockserver.state","wb") as f:
            pickle.dump(self.db,f)
            
    def calc_sig(self, methodname, args):
        sig="{}:{}:".format(self.testname,methodname)
        sig=sig.encode('utf8')+args[0].SerializeToString()
        signature=hashlib.sha256(sig).hexdigest()
        return signature
    
    def __getattr__(self, methodname):
        def rec_method(*args):
            signature=self.calc_sig(methodname,args)
            func=getattr(self.realserver,methodname)
            ret=func(args[0])
            payload=base64.b64encode(ret.SerializeToString())
            print("Called method: {},\n\tHASH: {}\n\tPayload: {}".format(methodname,signature,payload))
            self.db[signature]=(str(type(ret)),payload)
            self.save_state()
            return ret
        
        def play_method(*args):
            signature=self.calc_sig(methodname,args)
            payload=self.db[signature]
            print("Called method: {},\n\tHASH: {}\n\tPayload: {}".format(methodname,signature,payload))
            # "<class 'schema_pb2.VerifiableEntry'>" -> schema_pb2.VerifiableEntry
            cname=payload[0].split("'")[1] 
            ret=eval(cname)()
            ret.MergeFromString(base64.b64decode(payload[1]))
            return ret
        if self.mode==MODE_REC:
            return rec_method
        else:
            return play_method

from LedgerCompliance.client import Client
class MockClient(Client):
    def __init__(self, apikey: str, host: str, port: int, secure:bool=True):
        Client.__init__(self, apikey, host, port, secure)
        self.mockserver=MockServer(MODE, self._Client__stub)
        self._Client__stub=self.mockserver
        self._testname=None
        
    def set_interceptor(self, apikey):
        t=Client.set_interceptor(self,apikey)
        self.mockserver=MockServer(MODE, t)
        self.mockserver.testname=self._testname
        return self.mockserver
    
    def testname(self, name):
        self._testname=name
        self.mockserver.testname=name
