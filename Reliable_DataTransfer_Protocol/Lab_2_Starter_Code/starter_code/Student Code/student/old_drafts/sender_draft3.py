#!/usr/bin/env python3
from monitor import Monitor, format_packet, unformat_packet
import sys, configparser, time, threading

class Sender:
    def __init__(self, config_path):
        
        # self.RTT_Est         = 1.0
        # self.RTT_Dev         = 0.5
        # self.alpha           = 0.125
        # self.beta            = 0.25

        self.config_path = config_path
        self.send_monitor = Monitor(config_path, 'sender')
        self.cfg = configparser.RawConfigParser(allow_no_value=True)
        self.cfg.read(self.config_path)

        self.receiver_id 	 = int(self.cfg.get('receiver', 'id'))
        self.sender_id 		 = int(self.cfg.get('sender', 'id'))
        self.file_to_send 	 = self.cfg.get('nodes', 'file_to_send')
        self.max_packet_size = int(self.cfg.get('network', 'MAX_PACKET_SIZE'))

        self.window_size 	 = int(self.cfg.get('sender', 'window_size'))
        self.window_start 	 = 0
        self.packets 	 	 = []        
        
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

        self.send_thread.start()
        self.ack_thread.start()
        self.send_thread.join()
        self.ack_thread.join()

        time.sleep(0.73)
        self.send_monitor.send_end(self.receiver_id)

    def Send_Packets_Thread(self):  
        while self.window_start < len(self.packets):
            window_end = min(len(self.packets), self.window_start + self.window_size)
            for id in range(self.window_start, window_end):
                packet = f"{id} ".encode('ascii') + self.packets[id]
                self.send_monitor.send(self.receiver_id, 
                                       format_packet(self.sender_id, self.receiver_id, packet))
            time.sleep(0.44)
    
    def Receive_Ack_Thread(self):
        while self.window_start < len(self.packets):
            ack_id = self.Wait_For_Ack()
            if (ack_id is not None) and (ack_id >= self.window_start):
                self.window_start = ack_id + 1

    def Wait_For_Ack(self):
        
        while True:
            try:
                _, ack_data = self.send_monitor.recv(self.max_packet_size - 10)
                ack_msg = unformat_packet(ack_data)[1]
                ack_id = int(ack_msg.split()[1])
                # if ack_msg == f"NACK":
                #     return None
                return ack_id
            except:
                return None
		
if __name__ == '__main__':
    
	# Initialize the Config File
	print("Sender starting up!")
	config_path = sys.argv[1]

	# Initialize the sender
	sender = Sender(config_path)
	sender.send_thread = threading.Thread(target=sender.Send_Packets_Thread)
	sender.ack_thread = threading.Thread(target=sender.Receive_Ack_Thread)
	sender.Read_Text()