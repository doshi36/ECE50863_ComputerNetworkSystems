#!/usr/bin/env python3
from monitor import Monitor, unformat_packet, format_packet
import sys, configparser, time, threading

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
		
		self.lock = threading.Lock()
		self.expected_packet  = 0
		self.received_packets = [""]*50
		self.window_size 	  = 43
		self.last_frame 	  = -10
		self.prev_read 		  = -1

	def Receive_Text_Thread(self):
		
		while True:
				_, data = self.recv_monitor.recv(self.max_packet_size - 12)
				packet_id, packet_data = unformat_packet(data)[1].split(b' ', 1)
				packet_id = int(packet_id)
    
				if packet_id <= self.window_size + self.prev_read:
					if (packet_id > self.prev_read):  
						if b'0811' in packet_data:
							self.last_frame = packet_id
						else:
							self.received_packets[packet_id - self.prev_read - 1] = packet_data
					self.expected_packet = self.received_packets.index("") + self.prev_read + 1
     
					while self.received_packets and self.received_packets[0] != "":
						self.write_location.write(self.received_packets[0])
						self.prev_read += 1
						self.received_packets = self.received_packets[1:] + [""]
      
					if packet_id != self.last_frame:
						self.recv_monitor.send(self.sender_id, format_packet(self.receiver_id, self.sender_id, f"ACK {packet_id} {self.expected_packet}".encode('ascii')))
      
				if self.prev_read == self.last_frame - 1:
					break
 
		self.write_location.close()
		self.recv_monitor.recv_end(self.write_fd, self.sender_id)
				
		for _ in range(4):
			self.recv_monitor.send(self.sender_id, format_packet(self.receiver_id, self.sender_id, f"ACK {self.last_frame} {self.last_frame}".encode('ascii'))
			)

if __name__ == '__main__':
	print("Receiver starting up!")
	config_path = sys.argv[1]
	receiver = Receiver(config_path)
	receiver.Receive_Text_Thread()