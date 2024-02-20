#!/usr/bin/env python3
from monitor import Monitor, format_packet, unformat_packet
import sys, configparser, time

class Sender:
	def __init__(self, config_path):
		
		self.config_path = config_path
		self.send_monitor = Monitor(config_path, 'sender')
		self.cfg = configparser.RawConfigParser(allow_no_value=True)
		self.cfg.read(self.config_path)
		
		self.receiver_id 	 = int(self.cfg.get('receiver', 'id'))
		self.sender_id 		 = int(self.cfg.get('sender', 'id'))
		self.file_to_send 	 = self.cfg.get('nodes', 'file_to_send')
		self.max_packet_size = int(self.cfg.get('network', 'MAX_PACKET_SIZE'))
		
		self.window_size 	 = int(self.cfg.get('sender', 'window_size'))
		self.packets 	 	 = []        
		self.send_monitor.socketfd.settimeout(0.5)
		
	def Read_Text(self):
		print("Sender: Reading file to send...")
		
		with open(self.file_to_send, 'rb') as file:
			print('Sender: Sending file in frames to receiver...')
   
			while True:
				file_data = file.read(self.max_packet_size - 15)
    
				if not file_data:
					break
				self.packets.append(file_data)
    
		self.Send_Packets()
		time.sleep(7)
		self.send_monitor.send_end(self.receiver_id)
  
	def Send_Packets(self):
     
		window_start = 0
  
		while window_start < len(self.packets):
			window_end = min(len(self.packets), window_start + self.window_size)
   
			for id in range(window_start, window_end):
				packet = f"{id} ".encode('ascii') + self.packets[id]
				self.send_monitor.send(self.receiver_id, format_packet(self.sender_id, self.receiver_id, packet))

			acknowledge = self.Wait_For_Ack(window_start)
   
			if acknowledge is not None:
				window_start = acknowledge + 1
    
			else:
				window_start = window_start

	def Wait_For_Ack(self, expected_ack):
     
		while True:
			try:
				_, ack_data = self.send_monitor.recv(self.max_packet_size - 15)
				ack_msg = unformat_packet(ack_data)[1]
				ack_id = int(ack_msg.split()[1])
    
				if ack_id == expected_ack:
					return ack_id

			except:
				return None
		
if __name__ == '__main__':
    
    # Initialize the Config File
    print("Sender starting up!")
    config_path = sys.argv[1]
    
    # Initialize the sender
    sender = Sender(config_path)
    sender.Read_Text()
    
    

