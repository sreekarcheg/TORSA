'''
Authors: Sreekar Reddy, Akshita Mittel, Surya Teja Chavali
Contact: [cs13b1008, cs13b1028, cs13b1040]@iith.ac.in
License: MIT License
'''

"""
This program is the Client (sender), which sends the program over the TOR network to the server.
"""
from socket import *
from threading import Thread

#This is client's code and its completely naive about the protocol of onion routing.
#It intially sends destination address to Application proxy and begins the conversation thereafter.

DESTNADDR = ('127.0.0.1',9000)
APPNPROXY = ('127.0.0.1',8500)
SELFADDR = ('127.0.0.1',8000)

class Client:

	def __init__(self,selfAddr,destAddr):
		'''
		The sockets are initilised and the destination address is initilised to the proxy instead of the server.
		A timeout is set wherein the acknowledgement should be received.
		'''
		self.selfAddr=selfAddr
		self.destAddr=destAddr
		self.sock=socket(AF_INET,SOCK_DGRAM)
		self.sock.bind(self.selfAddr)
		self.sock.settimeout(10)
	
	def send_data(self,data):
		'''
		This function simply sends the data to the App-Proxy
		'''
		self.sock.sendto(data,self.destAddr)
		print 'Data sent to server::',data

	def recv_data(self,inp):
		'''
		This function listens to the responses from the App-Proxy. 
		If it timesout, it sends the message over and over.
		'''
		while True:
			try:
				data,addr=self.sock.recvfrom(1024)
				break
			except timeout:
				print "Ack not received...sending again"
				self.send_data(inp)
		print 'Data recieved from server :: ',data
	
	def close_connection(self):
		self.sock.close()
		
		
if __name__=='__main__':
	c=Client(SELFADDR,APPNPROXY)
	inp=str(DESTNADDR)
	c.send_data(inp)

	while True:
		inp=raw_input()
		c.send_data(inp)
		if(inp=='Disconnect'):
			print 'Disconnected'
			break
		else:
			c.recv_data(inp)
		
	c.close_connection()
