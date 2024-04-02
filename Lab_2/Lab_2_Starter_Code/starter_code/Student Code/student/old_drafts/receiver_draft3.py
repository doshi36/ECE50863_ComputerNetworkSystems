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
		
		self.expected_packet  = 0
		self.last_frame 	  = 0
		self.prev_read 		  = -1
		self.received_packets = {}

		self.lock = threading.Lock()

	def Receive_Text_Thread(self):
		
		while True:
      
			# Receive a packet from the sender
			_, data = self.recv_monitor.recv(self.max_packet_size - 12)
			packet_id, packet_data = unformat_packet(data)[1].split(b' ', 1)
			packet_id = int(packet_id)
   
			# If you receive the correct packet, store it inside the Rx buffer
			if packet_id == self.expected_packet:    
				if packet_data == b'0811':
					self.last_frame = packet_id
					print("Last frame received")
					self.recv_monitor.recv_end(self.write_fd, self.sender_id)
					break
				print(f"Storing packet {packet_id}")
				self.received_packets[packet_id] = packet_data
				self.expected_packet += 1
			
			# If you receive a packet that is less than the expected packet, send an ACK
			if packet_id <= self.expected_packet:
				self.recv_monitor.send(self.sender_id, format_packet(self.receiver_id, self.sender_id, f"ACK {packet_id}".encode('ascii')))
			else:
				self.recv_monitor.send(self.sender_id, format_packet(self.receiver_id, self.sender_id, f"NACK {packet_id}".encode('ascii')))
    
		# Send an ACK for the last frame	
		for i in range(10):
			self.recv_monitor.send(self.sender_id, format_packet(self.receiver_id, self.sender_id, f"ACK {self.last_frame}".encode('ascii')))
   
	def Process_Text_Thread(self):
		print("Processing thread started")
		# Process the received packets by writing them to the file
		while True:
			if self.lock.acquire():
				for i in range(self.prev_read + 1, self.expected_packet):
						if i in self.received_packets:
							self.write_location.write(self.received_packets[self.expected_packet])
							print(f"Writing packet {i}")
							self.prev_read = i
				self.lock.release()
			if self.expected_packet == self.last_frame:
				break
		self.write_location.close()
		
if __name__ == '__main__':
	print("Receiver starting up!")
	config_path = sys.argv[1]
	receiver = Receiver(config_path)

	receiver.Receive_Thread = threading.Thread(target=receiver.Receive_Text_Thread)
	receiver.Process_Thread = threading.Thread(target=receiver.Process_Text_Thread)
 
	receiver.Receive_Thread.start()
	receiver.Process_Thread.start()
	receiver.Receive_Thread.join()
	receiver.Process_Thread.join()
	