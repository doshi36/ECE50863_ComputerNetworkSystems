#!/usr/bin/env python3
from monitor import Monitor, format_packet, unformat_packet
import sys, configparser, time, threading

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
		
		self.window_size 	 = 40
		self.window_start 	 = 0
		self.packets 	 	 = []   
		self.received_acks   = {}
		
	def Read_Text(self):
		print("Sender: Reading file to send...")
		
		with open(self.file_to_send, 'rb') as file:
			print('Sender: Sending file in frames to receiver...')
			while True:
				file_data = file.read(self.max_packet_size - 12)
				if not file_data:
					break
				self.packets.append(file_data)
			self.packets.append(b'0811')
		print("Size of packets: ", len(self.packets))

		self.send_thread.start()
		self.ack_thread.start()
		self.send_thread.join()
		self.ack_thread.join()
		self.send_monitor.send_end(self.receiver_id)
  
	def Send_Packets_Thread(self):  
		while self.window_start < len(self.packets):
			window_end = min(len(self.packets), self.window_start + self.window_size)
			for id in range(self.window_start, window_end):
				if id in self.received_acks:
					continue
				packet = f"{id} ".encode('ascii') + self.packets[id]
				self.send_monitor.send(self.receiver_id, format_packet(self.sender_id, self.receiver_id, packet))
			if self.window_start == len(self.packets) - 1:
				break
			time.sleep(0.44)

	def Receive_Ack_Thread(self):
		ack_dict = {i:0 for i in range(len(self.packets))}

		while self.window_start < len(self.packets):
			curr_ack_id,next_expected_ack_id = self.Wait_For_Ack()
			self.received_acks[curr_ack_id] = True
			if (next_expected_ack_id > self.window_start):
				self.window_start = next_expected_ack_id

			ack_dict[next_expected_ack_id] += 1
			if ack_dict[next_expected_ack_id] == 3:
				# for i in range(1):
				self.send_monitor.send(self.receiver_id, format_packet(self.sender_id, self.receiver_id, f"{next_expected_ack_id} ".encode('ascii') + self.packets[next_expected_ack_id]))
			if next_expected_ack_id == len(self.packets) - 1:
				break

	def Wait_For_Ack(self):
		
		while True:
			try:
				_, ack_data = self.send_monitor.recv(self.max_packet_size - 10)
				ack_msg = unformat_packet(ack_data)[1]
				curr_ack_id = int(ack_msg.split()[1])
				next_expected_ack_id = int(ack_msg.split()[2])
				return (curr_ack_id, next_expected_ack_id)
			except:
				return (None,None)

		
if __name__ == '__main__':
    
	# Initialize the Config File
	print("Sender starting up!")
	config_path = sys.argv[1]

	# Initialize the sender
	sender = Sender(config_path)
	sender.send_thread = threading.Thread(target=sender.Send_Packets_Thread)
	sender.ack_thread = threading.Thread(target=sender.Receive_Ack_Thread)
	sender.Read_Text()

