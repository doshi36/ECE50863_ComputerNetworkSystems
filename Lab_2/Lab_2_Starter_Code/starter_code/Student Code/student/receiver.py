#!/usr/bin/env python3
from monitor import Monitor, unformat_packet, format_packet
import sys, configparser

class Receiver:
	def __init__(self, config_path):
		self.config_path 	  = config_path
		self.recv_monitor     = Monitor(config_path, 'receiver')
		self.cfg 			  = configparser.RawConfigParser(allow_no_value=True)
		self.cfg.read(self.config_path)
		
		self.sender_id 	      = int(self.cfg.get('sender', 'id'))
		self.receiver_id 	  = int(self.cfg.get('receiver', 'id'))
		self.max_packet_size  = int(self.cfg.get('network', 'MAX_PACKET_SIZE'))
		
		self.write_fd 		  = self.cfg.get('receiver', 'write_location')
		self.write_location   = open(self.write_fd, 'wb')
		
		self.expected_packet  = 0
		self.received_packets = {}
		self.recv_monitor.socketfd.settimeout(5)

	def Receive_Text(self):
		
		while True:
			try:
				_, data = self.recv_monitor.recv(self.max_packet_size - 15)
				packet_id, packet_data = unformat_packet(data)[1].split(b' ', 1)
				packet_id = int(packet_id)
				
				if packet_id == self.expected_packet:
					self.write_location.write(packet_data)
					self.expected_packet += 1

				self.recv_monitor.send(
        								self.sender_id, 
                           				format_packet(self.receiver_id, self.sender_id, f"ACK {packet_id}".encode('ascii'))
                               		  )
				
			except:
       
				print(f"Error or timeout receiving data")
				self.write_location.close()
				self.recv_monitor.recv_end(self.write_fd, self.sender_id)
				break     
		

if __name__ == '__main__':
    print("Receiver starting up!")
    config_path = sys.argv[1]
    receiver = Receiver(config_path)
    receiver.Receive_Text()
