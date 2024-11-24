#!/usr/bin/env python3
from monitor import Monitor, format_packet, unformat_packet
import sys
import time
from datetime import date, datetime

# Config File
import configparser

class Sender:
	def __init__(self, config_path):
     
		self.config_path  = config_path
		self.send_monitor = Monitor(config_path, 'sender')
		self.send_monitor.socketfd.settimeout(0.3)
  
		self.all_frames   = {} # {F_ID : F_ID Frame}
  
		cfg = configparser.RawConfigParser(allow_no_value=True)
		cfg.read(self.config_path)

		self.receiver_id 	 = int(cfg.get('receiver', 'id'))
		self.sender_id 		 = int(cfg.get('sender', 'id'))
		self.file_to_send 	 = cfg.get('nodes', 'file_to_send')
		self.max_packet_size = int(cfg.get('network', 'MAX_PACKET_SIZE'))
		self.F_ID 			 = 0

	def Read_Text(self):
		print('Sender: Reading file to send...')
  
		with open(self.file_to_send, 'rb') as file:
			print('Sender: Sending file in frames to receiver...')
   
			while file:
				file_data = file.read(self.max_packet_size - 15)
				if file_data:
					frame_to_send = f"{self.F_ID} ".encode('ascii') + file_data
					self.Send_Packet(frame_to_send)
				else:
					break  
		time.sleep(7)
		self.send_monitor.send_end(self.receiver_id)
  
	def Send_Packet(self, frame_to_send):
		
		# Send the frame to the receiver
		self.all_frames[self.F_ID] = frame_to_send
		self.send_monitor.send(self.receiver_id, format_packet(self.sender_id, self.receiver_id, frame_to_send))
		
  		# Set the ACK_FLAG to False
		ACK_FLAG = False
  
        # Wait for the ACK
		while ACK_FLAG == False:
			try:
				(_, data) = self.send_monitor.recv(self.max_packet_size-15)
				data = unformat_packet(data)[1]
				ACK_FLAG = True if (data == f"ACK {self.F_ID}".encode('ascii')) else False
			except:
				self.send_monitor.send(self.receiver_id, format_packet(self.sender_id, self.receiver_id, self.all_frames[self.F_ID]))

		self.F_ID += 1

if __name__ == '__main__':
	
	# Initialize Config File
	print("Sender starting up!")
	config_path = sys.argv[1]

	# Initialize sender
	sender = Sender(config_path)
	sender.Read_Text()
