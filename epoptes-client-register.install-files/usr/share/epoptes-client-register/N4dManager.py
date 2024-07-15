import xmlrpc.client
import ssl
import threading
import time
import n4d.client


import os


class N4dManager:

	
	def __init__(self,server=None):
		
		self.debug=True
		
		self.user_validated=False
		self.client=None
		self.user_val=()
		self.user_groups=[]
		self.validation=None

		#self.core = n4d.server.core.Core.get_core()

		if server!=None:
			self.set_server(server)
		
	#def init
	



	def mprint(self,msg):
		
		if self.debug:
			print("[EpoptesClientRegisterN4DManager] %s"%str(msg))
			
	#def mprint
		
	



	def set_server(self,server):
		
		#context=ssl._create_unverified_context()	
		#self.client=xmlrpc.client.ServerProxy("https://%s:9779"%server,allow_none=True,context=context)

		self.server="https://%s:9779"%server
		self.mprint("Proxy: %s"%self.client)
		
	#def set_server



	
	
	def validate_user(self,user,password):
		
		'''ret=self.client.validate_user(user,password)
		self.user_validated,self.user_groups=ret
			
		
		if self.user_validated:
			self.user_val=(user,password)
		
		return [self.user_validated, self.user_val]'''
		try:
			self.client=n4d.client.Client(self.server,user,password)

			ret=self.client.validate_user()
			self.user_validated=ret[0]
			self.user_groups=ret[1]
			self.credentials=[user,password]
		
			if self.user_validated:
				session_user=os.environ["USER"]
				self.ticket=self.client.get_ticket()
				if self.ticket.valid():
					self.client=n4d.client.Client(ticket=self.ticket)
					msg_log="Session User: %s"%session_user+" EpoptesClientRegister User: %s"%user
					self.mprint(msg_log)
					
					self.local_client=n4d.client.Client("https://localhost:9779",user,password)
					local_t=self.local_client.get_ticket()
					if local_t.valid():
						self.local_client=n4d.client.Client(ticket=local_t)
					else:
						self.user_validated=False	
				else:
					self.user_validated=False
			self.mprint(self.user_groups)

		except Exception as e:
			msg_log="(validate_user)Session User Error: %s"%(str(e))
			self.mprint(msg_log)
			self.user_validated=False
	
		
	#def validate_user



	def get_variable (self,N4D_VAR):
		
		try:
			self.mprint('(get_variable) Call N4D function..')
			self.variable=self.local_client.get_variable(N4D_VAR)
			self.mprint('(get_variable) VAR is: %s'%self.variable)
			return [True,self.variable]
		
		except Exception as e:
			self.mprint(e)
			return [False, "Error get_variable"]
		
	#def get_value
	
	
	
	def set_variable (self,N4D_VAR,dict_var):
		
		try:
			solved=self.local_client.set_variable(N4D_VAR,dict_var)
			self.mprint('(set_variable) %s'%solved)
			if solved:
				return True
			else:
				return False
		
		except Exception as e:
			self.mprint(e)
			return False
		
	#def set_variable

