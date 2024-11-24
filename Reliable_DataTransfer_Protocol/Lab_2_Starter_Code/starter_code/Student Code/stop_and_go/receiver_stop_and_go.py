#!/usr/bin/env python3
from monitor import Monitor, unformat_packet, format_packet
import sys

# Config File
import configparser

class Receiver:
	def __init__(self, config_path):
		self.config_path  = config_path
		self.recv_monitor = Monitor(config_path, 'receiver')
		self.recv_monitor.socketfd.settimeout(5)

		cfg = configparser.RawConfigParser(allow_no_value=True)
		cfg.read(config_path)
  
		self.sender_id 		 = int(cfg.get('sender', 'id'))
		self.receiver_id     = int(cfg.get('receiver', 'id'))

		self.max_packet_size = int(cfg.get('network', 'MAX_PACKET_SIZE'))
		self.write_fd  = cfg.get('receiver', 'write_location')
		self.write_location  = open(self.write_fd, 'wb')
  
		self.recvd_frame     = {} #{F_ID: True or False}
		self.F_ID			 = 0

	def Receive_Text(self):
     
		while True:
			try:
				(_, data) 	= self.recv_monitor.recv(self.max_packet_size - 15)
				_, data = unformat_packet(data)

				id_recvd = int(data.split(b" ")[0])
				frame 	 = data.split(b" ",1)[1]

				if id_recvd == self.F_ID and id_recvd not in self.recvd_frame:
			
					self.F_ID += 1
					self.recvd_frame[id_recvd] = True
					self.write_location.write(frame)

				# Send ACK
				self.recv_monitor.send(self.sender_id, format_packet(self.receiver_id, self.sender_id, f"ACK {id_recvd}".encode('ascii')))
    
			except:
				self.write_location.close()
				self.recv_monitor.recv_end(self.write_fd, self.sender_id)
				break

		
if __name__ == '__main__':

	# Initialize Config File=
	# print("Receivier starting up!")
	config_path = sys.argv[1]

	# Initialise Receiver
	receiver = Receiver(config_path)
	receiver.Receive_Text()
	