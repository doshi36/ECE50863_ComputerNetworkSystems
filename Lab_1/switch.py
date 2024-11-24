#!/usr/bin/env python

"""This is the Switch Starter Code for ECE50863 Lab Project 1
Author: Xin Du
Email: du201@purdue.edu
Last Modified Date: December 9th, 2021
"""

import sys
import socket
import time
import threading
from datetime import date, datetime

# Please do not modify the name of the log file, otherwise you will lose points because the grader won't be able to find your log file
LOG_FILE = "switch#.log" # The log file for switches are switch#.log, where # is the id of that switch (i.e. switch0.log, switch1.log). The code for replacing # with a real number has been given to you in the main function.
LINK_FAIL = False
NEIGHBOUR_ID = -9999

# Those are logging functions to help you follow the correct logging standard

# "Register Request" Format is below:
#
# Timestamp
# Register Request Sent

def register_request_sent():
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Register Request Sent\n")
    write_to_log(log)

# "Register Response" Format is below:
#
# Timestamp
# Register Response Received

def register_response_received():
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Register Response received\n")
    write_to_log(log) 

# For the parameter "routing_table", it should be a list of lists in the form of [[...], [...], ...]. 
# Within each list in the outermost list, the first element is <Switch ID>. The second is <Dest ID>, and the third is <Next Hop>.
# "Routing Update" Format is below:
#
# Timestamp
# Routing Update 
# <Switch ID>,<Dest ID>:<Next Hop>
# ...
# ...
# Routing Complete
# 
# You should also include all of the Self routes in your routing_table argument -- e.g.,  Switch (ID = 4) should include the following entry: 		
# 4,4:4

def routing_table_update(routing_table):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append("Routing Update\n")
    for row in routing_table:
        log.append(f"{row[0]},{row[1]}:{row[2]}\n")
    log.append("Routing Complete\n")
    write_to_log(log)

# "Unresponsive/Dead Neighbor Detected" Format is below:
#
# Timestamp
# Neighbor Dead <Neighbor ID>

def neighbor_dead(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Neighbor Dead {switch_id}\n")
    write_to_log(log) 

# "Unresponsive/Dead Neighbor comes back online" Format is below:
#
# Timestamp
# Neighbor Alive <Neighbor ID>

def neighbor_alive(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Neighbor Alive {switch_id}\n")
    write_to_log(log) 

def write_to_log(log):
    with open(LOG_FILE, 'a+') as log_file:
        log_file.write("\n\n")
        # Write to log
        log_file.writelines(log)
        
class SwitchClient:
    def __init__(self, switch_id, controller_hostname, controller_port):
        self.switch_id           = switch_id
        self.controller_hostname = controller_hostname
        self.controller_port     = controller_port
        self.switch_socket       = None
        self.neighbour_specs     = {} # {neighbour_id: (neighbour_hostname, neighbour_port, neighbour_status)}
        self.counter             = {}
    
    def SendRegisterRequest(self):
        print("Creating switch socket...")
        self.switch_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.switch_socket.sendto(f"{self.switch_id} Register_Request".encode("utf-8"), 
                                  (self.controller_hostname, self.controller_port))
        print(f"{self.switch_id} Register_Request")
        register_request_sent()
    
    def RcvResponse(self):
        
        (data, client_addr) = self.switch_socket.recvfrom(1024)
        decoded_data = data.decode('utf-8').split('\n')
        register_response_received()
        
        for d in decoded_data[1:]:
            if (len(d.split()) == 3):
                neighbour_id, neighbour_hostname, neighbour_port = d.split()
                self.neighbour_specs[int(neighbour_id)] = {
                                                "Neighbour_Hostname": neighbour_hostname, 
                                                "Neighbour_Port":     int(neighbour_port), 
                                                "Status":             True
                                                }
                self.counter[int(neighbour_id)] = time.time()

    def KeepListening(self):
        K = 2
        TIMEOUT = K * 3
        
        while True:
            (data, neigh_addr) = self.switch_socket.recvfrom(1024)
            decoded_data_id = int(data.decode('utf-8').split()[0])
            msg             = data.decode('utf-8').split()[1]
            if (msg == "KEEP_ALIVE" and (LINK_FAIL != True or int(decoded_data_id) != NEIGHBOUR_ID)):
                self.counter[int(decoded_data_id)] = time.time()
                if(self.neighbour_specs[decoded_data_id]["Status"] == False): 
                    neighbor_alive(decoded_data_id)
                    self.neighbour_specs[decoded_data_id]["Status"]             = True
                    self.neighbour_specs[decoded_data_id]["Neighbour_Hostname"] = (neigh_addr[0])
                    self.neighbour_specs[decoded_data_id]["Neighbour_Port"]     = int(neigh_addr[1])
                    self.TopologyUpdate()
                    
                for neighbour_id, last_time in self.counter.items():
                    if time.time() - last_time > TIMEOUT and self.neighbour_specs[neighbour_id]["Status"] == True:
                        self.neighbour_specs[neighbour_id]["Status"] = False
                        neighbor_dead(neighbour_id)
                        self.TopologyUpdate()
                        
            elif (msg != "KEEP_ALIVE"):
                my_data = data.decode('utf-8').split('\n')  
                routing_log = []
                for d in my_data[1:]:
                    s, de, h = d.split()
                    routing_log.append([s, de, h])
                routing_table_update(routing_log)
                
    def TopologyUpdate(self):
        message_lines = [str(self.switch_id)]
        
        for neighbor_id, status in self.neighbour_specs.items():
            status_str = 'True' if status["Status"] == True else 'False'
            message_lines.append(f"{neighbor_id} {status_str}")

        message = "\n".join(message_lines)
        self.switch_socket.sendto(message.encode(), (self.controller_hostname, self.controller_port))
            
    def KeepAlive(self):
        while True:
            for neighbour_id, status in self.neighbour_specs.items():
                if (LINK_FAIL != True or int(neighbour_id) != NEIGHBOUR_ID):
                    self.switch_socket.sendto(f"{self.switch_id} KEEP_ALIVE".encode(), 
                                            (status["Neighbour_Hostname"], 
                                            status["Neighbour_Port"]))
            self.TopologyUpdate()
            time.sleep(2)
        
def main():

    global LOG_FILE
    #Check for number of arguments and exit if host/port not provided
    num_args = len(sys.argv)
    if num_args < 4:
        print ("switch.py <Id_self> <Controller hostname> <Controller Port>\n")
        sys.exit(1)

    my_id    = int(sys.argv[1])
    LOG_FILE = 'switch' + str(my_id) + ".log" 
    
    # Write your code below or elsewhere in this file
    K = 2

    controller_hostname, controller_port = sys.argv[2], int(sys.argv[3])
    switch = SwitchClient(my_id, controller_hostname, controller_port)
    
    switch.SendRegisterRequest()
    switch.RcvResponse()
    
    global LINK_FAIL
    global NEIGHBOUR_ID
    
    if (num_args == 4):
        LINK_FAIL = False
        NEIGHBOUR_ID = -9999
    else:
        if(sys.argv[4] == "-f"):
            LINK_FAIL = True
            NEIGHBOUR_ID = int(sys.argv[5])
    
    keep_listening_thread = threading.Thread(target = switch.KeepListening)
    keep_listening_thread.start()
    keep_alive_thread     = threading.Thread(target = switch.KeepAlive)
    keep_alive_thread.start()
    
        
if __name__ == "__main__":
    main()