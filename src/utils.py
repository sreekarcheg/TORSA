'''
Authors: Sreekar Reddy, Akshita Mittel
Contact: [cs13b1008, cs13b1028]@iith.ac.in
License: MIT License
'''

from Crypto.Cipher import AES
from Crypto import Random
import string

#This files contains some common functions which are frequently used in other files.
#This utility file is to be imported in each code.
common_iv = b"0000000000000000"

def convert_message(message):
	'''
	This converts the messages into its components as specified by the return type.
	'''
	temp = message.partition('(')[2]
	temp1 = temp.partition(',')[0]
	temp2 = temp.partition(',')[2]
	ip = temp1.split("'")[1]
	port = string.atoi(temp2.partition(')')[0])
	data = temp2.partition(')')[2]
	return ((ip,port),data)
	
def encrypt_msg(key,message):
	'''
	The message is encrypted using AES. 
	The initialisation vector has to be the same for both the encryption and decryption, hence it is appended to the messgae. 
	'''
	encryptor = AES.new(key,AES.MODE_CBC, common_iv)
	return common_iv + encryptor.encrypt(message)

def decrypt_msg(key,message):
	'''
	The messages are decrypted using this function. 
	The IV key is stored in the first 16 bytes of the message.
	'''
	decryptor =AES.new(key,AES.MODE_CBC, message[ :16])
	return decryptor.decrypt(message[16:])
	
#Since AES standard requires strings to be in multiples of size 16, 
#that's why we need to pad  and unpad the message strings as when required.

def pad_string(data):
	if len(data)%16!=0:
		data=data+'$'*(16-len(data)%16)			#this is because AES encryptor requires message of length which is a multiple of 16
	return data
	
def unpad_string(data):
	data=data.partition('$')[0]
	return data
