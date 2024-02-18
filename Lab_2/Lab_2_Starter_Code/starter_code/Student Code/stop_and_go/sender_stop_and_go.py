#!/usr/bin/env python3
from monitor import Monitor
import sys
import time
import threading
from datetime import date, datetime

# Config File
import configparser

class Sender:
	def __init__(self, config_path):
		self.config_path  = config_path
		self.send_monitor = Monitor(config_path, 'sender')
		self.counter      = {}

		cfg = configparser.RawConfigParser(allow_no_value=True)
		cfg.read(self.config_path)

		self.receiver_id 	 = int(cfg.get('receiver', 'id'))
		self.file_to_send 	 = cfg.get('nodes', 'file_to_send')
		self.max_packet_size = int(cfg.get('network', 'MAX_PACKET_SIZE'))

	def Read_Text(self):
		print('Sender: Reading file to send.')
  
		with open(self.file_to_send, 'r') as file:
			file_data = file.read()
			file_data = file_data.split('\n')	
			self.Send_File(file_data)
   
		for frame in range(len(file_data)):
			self.Send_Line(frame)

	def Send_Line(self, frame):
		print('Sender: Sending file in frames to receiver.')
		self.send_monitor.send(self.receiver_id, frame.encode('utf-8'))
		self.counter[frame] = time.time()
		
		while self.Receive_Ack() == False:
			self.ResendFrame(frame)
    
		self.send_monitor.send_end(self.receiver_id)
  
	def ResendFrame(self, frame):
		self.send_monitor.send(self.receiver_id, frame.encode('utf-8'))
		self.counter[frame] = time.time()
		
		return self.Receive_Ack()

	def Receive_Ack(self):
		(addr, data) = self.send_monitor.recv(self.max_packet_size)
		msg          = str(data.decode('utf-8'))
  
		ACK_FLAG = True if (msg == "ACK") else False
  
		return ACK_FLAG
	
	def Timeout_Handler(self):
		TIMEOUT = 3  
  
		while True:
			for frame in self.counter:
				if (time.time() - self.counter[frame] > TIMEOUT):
					self.ResendFrame(frame)

if __name__ == '__main__':
    
    # Initialize Config File
	print("Sender starting up!")
	config_path = sys.argv[1]

 	# Initialize sender
	sender = Sender(config_path)

	# Start sending the file
	sending_thread = threading.Thread(target = sender.Read_Text)
	sending_thread.start()

	# Start the timeout handler
	timeout_thread = threading.Thread(target = sender.Timeout_Handler)
	timeout_thread.start()