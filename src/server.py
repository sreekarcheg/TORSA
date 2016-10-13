'''
Authors: Sreekar Reddy, Akshita Mittel, Surya Teja Chavali
Contact: [cs13b1008, cs13b1028, cs13b1040]@iith.ac.in
License: MIT License
'''

"""
This file contains the code for receiver (server). Which receives the message from the sender.
"""
from socket import *
from utils import *
import sys
from select import select

#This is the code for server.
#Initially server is assigned a key through onion routing mechanism by Application Proxy as soon as connection is being opened from client side.
#As soon as server receives the data, it sends an acknowledgement to client before the timer gets over.

#To send message from server to client along with ack, enter message within 5 secs(timeout)
#else ack only will be send.

class Server:
	def __init__(self,selfAddr):
		self.selfAddr=selfAddr
		self.leftip=0
		self.sock=socket(AF_INET,SOCK_DGRAM)
		self.sock.bind(self.selfAddr)	
		data,addr=self.sock.recvfrom(1024)
		print "server data:", data
		if data[0:5] == '_key_':
			self.leftip=addr
			self.key=data[5:].split('_nextip_')[0]
				
	def send_data(self,data):
		print 'Data sent to client::',data
		data=pad_string(data)
		self.sock.sendto(encrypt_msg(self.key,data),self.leftip)
	
	def recv_data(self):
		data,addr=self.sock.recvfrom(1024)
		if data=='Disconnect':
			return data
		else:
			dataaux=decrypt_msg(self.key,data)
			msg=unpad_string(dataaux)
			print 'Data recieved from client :: ',msg
			return msg
	
	def close_connection(self):
		self.sock.close()	
	
		
		
if __name__=='__main__':
	s=Server(('127.0.0.1',9000))
		
	while True:
		data=s.recv_data()
		if data=='Disconnect':
			s.close_connection()
			break

		timeout = 5							#timer for server to wait for message
		print "Enter Server Message to client-"
		print "Entered:",
		rlist, _, _ = select([sys.stdin], [], [], timeout)
		if rlist:
			msg = sys.stdin.readline()
			print msg.rstrip()
			msg="Ack , ServerMsg: " + msg.rstrip()			#rstrip is to remove \n at end
		else:
			print "No input. Moving on..."
			msg="Ack , ServerMsg: NULL"
		s.send_data(msg)
				
	s.close_connection()
