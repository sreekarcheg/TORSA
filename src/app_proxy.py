'''
Authors: Sreekar Reddy, Akshita Mittel, Surya Teja Chavali
Contact: [cs13b1008, cs13b1028, cs13b1040]@iith.ac.in
License: MIT License
'''

"""
This file consists of the central authoritative unit.
The Application proxy has two main functionalities. 
These include the transfer of keys and encryption of messages.
"""
from socket import *
from Crypto.Cipher import AES
import random
import default_data
import string
import time
from utils import *

#At the initialization time, the list of onion routers is available to
#it. It then decides an appropiate sequence of onion routers in order to transmit the message from
#the source to the destination. It distributes the keys to each of the routers. After this, network is
#set up. At the time of client to server communication, it encrypts the message whereas during server
#to client communication, it decrypts it and passes it to client.


class App_proxy:

	def __init__(self, selfAddr, router_list1):
		'''
		Initialising the App_proxy object, setting the destination address.
		The TOR routers are decided here and the reordered to get the routing algorithm.
		A call is made to initialize all the keys.
		'''
		self.selfAddr = selfAddr
		self.sock = socket(AF_INET,SOCK_DGRAM)
		self.sock.bind(self.selfAddr)	
		data, self.clientAddr = self.sock.recvfrom(1024)
		self.destAddr = convert_message(data)[0]
		self.key_list = []
		self.server_key = 0
		self.router_list = router_list1
		random.shuffle(self.router_list)
		self.key_assign()

	def key_generate(self, size=16, chars = string.ascii_uppercase + string.digits):
		'''
		Each key is generated in this function. The randomised algorithm makes each key unique.
		'''
		return ''.join(random.choice(chars) for x in range(size))
	
	def key_assign(self):
		'''
		Assignming each router with a unique key.
		'''
		for i in range(len(self.router_list)):
			self.key_list.append(self.key_generate())
		self.server_key = self.key_generate()
		
	def key_transfer(self):
		'''
		The keys are transferred to each router as well as the server. 
		The method for transfer is defined as follows:
		'''

		# The router which is immediately after the client is sent the key and next router address without any encryption.
		if len(self.router_list)>1:
			self.sock.sendto('_key_' + self.key_list[0] + '_nextip_' + str(self.router_list[1]), self.router_list[0])
		else:
			self.sock.sendto('_key_' + self.key_list[0] + '_nextip_' + str(self.destAddr), self.router_list[0])

		# For all the other routers, each message is embedded within layers of encryption and sent th=o the first router.
		# The number of encryption layers is based on the distance of the router from the client.
		for i in range(1,len(self.router_list)):
			if i == len(self.router_list) - 1:
				msg = '_key_' + self.key_list[i] + '_nextip_' + str(self.destAddr)
			else:
				msg = '_key_' + self.key_list[i] + '_nextip_' + str(self.router_list[i+1])
			for j in range(i-1,-1,-1):
				msg = encrypt_msg(self.key_list[j], msg)
			self.sock.sendto(msg, self.router_list[0])

		# Finally the key is sent to the server.
		server_msg = '_key_' + self.server_key + '_nextip_' + str(self.destAddr)
		for j in range(len(self.router_list)-1, -1, -1):
				server_msg = encrypt_msg(self.key_list[j], server_msg)
		self.sock.sendto(server_msg, self.router_list[0])

		
		
	def send_data(self,data):
		'''
		The data is padded so that it is a multiple of 16 bytes. 
		it is then encrypted based on the keys of ALL routers 
		Afterwhich it is sent to the first TOR router
		'''
		data = '_key_' + data
		data = pad_string(data)
		data = encrypt_msg(self.server_key,data)
		for i in range(len(self.key_list)-1, -1, -1):
			data=encrypt_msg(self.key_list[i], data)
		self.sock.sendto(data, self.router_list[0])
			
	def decrypt_server_data(self,msg):
		'''
		The acknowledgement from the server is encrypted through all the routers. 
		Before it is sent to the client it has to be decrypted off all its layers.
		'''
		for j in range(len(self.router_list)):
			msg=decrypt_msg(self.key_list[j], msg)
		msg=decrypt_msg(self.server_key, msg)
		return msg
	
	def recv_data(self):
		'''
		If the message received from the client is Disconnect. The message is passed on to all the routers and the socket is closed.
		Else it is encrypted and sent to the first router as explained above.
		If the message is received from the server it is decrypted and passed onto the client.
		'''
		data, addr=self.sock.recvfrom(1024)
		if addr == self.clientAddr:
			print 'Data recieved from client :: ', data
			if data == 'Disconnect':
				for i in range(len(self.router_list)):
					self.sock.sendto(data, self.router_list[i])
				self.sock.sendto(data, self.destAddr)
				return 0
			else:
				self.send_data(data)
				return 1
		else:
			msgaux = self.decrypt_server_data(data)
			msg = unpad_string(msgaux)
			print 'Data recieved from server :: ', msg
			self.sock.sendto(msg, self.clientAddr)
			return 1
			
	def close_connection(self):
		self.sock.close()	

		
if __name__ == '__main__':
	c=App_proxy(('127.0.0.1',8500), default_data.router_list)
		
	inp = raw_input()
	if inp == 'Connect':
		c.key_transfer()
		print "Successfully distributed keys"
	while True:
		if(c.recv_data() == 0):
			break
	c.close_connection()
