'''
Authors: Sreekar Reddy, Akshita Mittel, Surya Teja Chavali
Contact: [cs13b1008, cs13b1028, cs13b1040]@iith.ac.in
License: MIT License
'''

"""
This is one of the TOR routers. 
"""
from socket import *
from Crypto.Cipher import AES
import string
from utils import *

#This is the code for intermediate path routers.
#In the initialisation part all the routers are given their kyer using onion routing key assignment then
#at that time they store their prev and next node address, which they use for further transmission till the user calls off

class Router:
	def __init__(self,selfAddr):
		'''
		First the router creates a socket and binds to its own address. It then waits and listens for information.
		The router is initialised with its adjacent edges and key as soon as it receives its first message.
		'''
		self.selfAddr=selfAddr
		self.sock=socket(AF_INET,SOCK_DGRAM)
		self.sock.bind(self.selfAddr)
		data,addr=self.sock.recvfrom(1024)
		print "data:", data
		if data[0:5] == '_key_':
			self.prevAddr=addr
			self.key=data[5:].split('_nextip_')[0]
			self.nextAddr=convert_message(data[5:].split('_nextip_')[1])[0]

	
	def send_data(self,data,addr):
		'''
		The data is simply passed on to the next router
		'''
		self.sock.sendto(data,addr)
		print 'Data sent ::',data
	
	def recv_data(self):
		'''
		If the message recieved is Disconnect then we close the connection. 
		If the message is received from the previous address in the path a layer of encryption is removed.
		If the message is received from the subsequent address in the path a layer of encryption is added.
		'''
		data,addr=self.sock.recvfrom(1024)
		if data=='Disconnect':
			return 0
		else:
			if addr==self.prevAddr:
				data_forward=decrypt_msg(self.key,data)
				print 'Data recieved from client :: ',data_forward
				self.send_data(data_forward,self.nextAddr)
			if addr==self.nextAddr:
				data_reverse=encrypt_msg(self.key,data)
				print 'Data recieved from server :: ',data_reverse
				self.send_data(data_reverse,self.prevAddr)
			return 1
	
	def close_connection(self):
		self.sock.close()
		
		
if __name__=='__main__':
	r=Router(('127.0.0.1',6100))
		
	while True:
		if(r.recv_data()==0):
			break
				
	r.close_connection()
