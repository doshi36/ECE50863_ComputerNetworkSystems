#!/usr/bin/env python3
from monitor import Monitor
import sys

# Config File
import configparser

class Receiver:
	def __init__(self, config_path):
		self.config_path  = config_path
		self.recv_monitor = Monitor(config_path, 'receiver')

		cfg = configparser.RawConfigParser(allow_no_value=True)
		cfg.read(config_path)
  
		self.sender_id 		 = int(cfg.get('sender', 'id'))
		self.write_location  = cfg.get('receiver', 'write_location')
		self.write_location  = open(self.write_location, 'w')
		self.max_packet_size = int(cfg.get('network', 'MAX_PACKET_SIZE'))
		self.frames          = {} #{frame: "True" or "False"}
	
	def Receive_Text(self):
     
		while True:
			(addr, data) = self.recv.recv(self.max_packet_size)
			frame = str(data.decode('utf-8'))
		
			if frame not in self.frames:
				self.frames[frame] = True
				self.write_location.write(frame)
			
			self.Send_Ack()
   
	    # TO DO: End the Receiver before the Sender
  		# self.recv_monitor.recv_end('received_file', self.sender_id)
			
	def Send_Ack(self):
		self.recv_monitor.send(self.sender_id, "ACK".encode('utf-8'))	
	
if __name__ == '__main__':
    
    # Initialize Config File
	print("Receivier starting up!")
	config_path = sys.argv[1]

	# Initialise Receiver
	receiver = Receiver(config_path)
	receiver.Receive_Text()
	