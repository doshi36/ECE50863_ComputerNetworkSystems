#!/usr/bin/env python

"""This is the Controller Code for ECE50863 Lab Project 1
Author: Parth R. Doshi
Email: doshi36@purdue.edu
"""

import sys
import socket
import heapq
import pickle
from collections import *
from datetime import date, datetime
import time

# Please do not modify the name of the log file, otherwise you will lose points because the grader won't be able to find your log file
LOG_FILE = "Controller.log"

# Those are logging functions to help you follow the correct logging standard

# "Register Request" Format is below:
#
# Timestamp
# Register Request <Switch-ID>

def register_request_received(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Register Request {switch_id}\n")
    write_to_log(log)

# "Register Responses" Format is below (for every switch):
#
# Timestamp
# Register Response <Switch-ID>

def register_response_sent(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Register Response {switch_id}\n")
    write_to_log(log) 

# For the parameter "routing_table", it should be a list of lists in the form of [[...], [...], ...]. 
# Within each list in the outermost list, the first element is <Switch ID>. The second is <Dest ID>, and the third is <Next Hop>, and the fourth is <Shortest distance>
# "Routing Update" Format is below:
#
# Timestamp
# Routing Update 
# <Switch ID>,<Dest ID>:<Next Hop>,<Shortest distance>
# ...
# ...
# Routing Complete
#
# You should also include all of the Self routes in your routing_table argument -- e.g.,  Switch (ID = 4) should include the following entry: 		
# 4,4:4,0
# 0 indicates ‘zero‘ distance
#
# For switches that can’t be reached, the next hop and shortest distance should be ‘-1’ and ‘9999’ respectively. (9999 means infinite distance so that that switch can’t be reached)
#  E.g, If switch=4 cannot reach switch=5, the following should be printed
#  4,5:-1,9999
#
# For any switch that has been killed, do not include the routes that are going out from that switch. 
# One example can be found in the sample log in starter code. 
# After switch 1 is killed, the routing update from the controller does not have routes from switch 1 to other switches.

def routing_table_update(routing_table):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append("Routing Update\n")
    for row in routing_table:
        log.append(f"{row[0]},{row[1]}:{row[2]},{row[3]}\n")
    log.append("Routing Complete\n")
    write_to_log(log)

# "Topology Update: Link Dead" Format is below: (Note: We do not require you to print out Link Alive log in this project)
#
#  Timestamp
#  Link Dead <Switch ID 1>,<Switch ID 2>

def topology_update_link_dead(switch_id_1, switch_id_2):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Link Dead {switch_id_1},{switch_id_2}\n")
    write_to_log(log) 

# "Topology Update: Switch Dead" Format is below:
#
#  Timestamp
#  Switch Dead <Switch ID>

def topology_update_switch_dead(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Switch Dead {switch_id}\n")
    write_to_log(log) 

# "Topology Update: Switch Alive" Format is below:
#
#  Timestamp
#  Switch Alive <Switch ID>

def topology_update_switch_alive(switch_id):
    log = []
    log.append(str(datetime.time(datetime.now())) + "\n")
    log.append(f"Switch Alive {switch_id}\n")
    write_to_log(log) 

def write_to_log(log):
    with open(LOG_FILE, 'a+') as log_file:
        log_file.write("\n\n")
        # Write to log
        log_file.writelines(log)

def process_config(graph_text):
    
    dij_graph = defaultdict(dict)
    
    try:
        file = open(graph_text, "r")
        num_switches = int(file.readline().strip())
        lines = file.readlines()
        
        # Create the adjacency matrix
        for line in lines:
            s1, s2, dist = map(int, line.strip().split())
            dij_graph[s1][s2] = {"Price": dist, "Status": "True"}
            dij_graph[s2][s1] = {"Price": dist, "Status": "True"}
        
        file.close()
        print(f"DijGraph {dij_graph}")
        return (num_switches, dij_graph)
    
    except FileNotFoundError:
        print(f"Error: File '{graph_text}' not found.")

class ControllerServer:
    
    def __init__(self, controller_port, num_switches, adj_matrix):
        self.controller_port   = controller_port # Port
        self.num_switches      = num_switches    # Number of switches
        self.adj_matrix        = adj_matrix      # Adjacency Matrix
        self.switch_specs      = {}              # Switch_ID: Switch_HostName, Switch_Port, Alive/Dead
        self.controller_socket = None            # Controller socket
        self.counter           = {}              # Counter for each switch
        
    def path_computation(self):
        cumulative_short_path = {} 
        
        for track_src in range(0, self.num_switches):
            edge_weight = {edge: int('9999') for edge in range(0, self.num_switches)}
            edge_weight[track_src] = 0
            next_hops = {edge: [] for edge in range(self.num_switches)} 
            p_q = [(0, track_src)]

            while (p_q):
                current_dist, curr_edge = heapq.heappop(p_q)

                if current_dist <= edge_weight[curr_edge]:
                    for neighbor, weight in self.adj_matrix[curr_edge].items():
                        if weight["Status"] == "True" and self.switch_specs[neighbor]["Status"] == True:
                            new_dist = edge_weight[curr_edge] + weight["Price"]
                            if new_dist < edge_weight[neighbor]:
                                edge_weight[neighbor] = new_dist
                                next_hops[neighbor] = next_hops[curr_edge] + [curr_edge]
                                # print(f"{track_src} Next Hops: {next_hops[neighbor]}")
                                heapq.heappush(p_q, (new_dist, neighbor))

            smallest_paths = {edge: edge_weight[edge] for edge in range(0, self.num_switches)}
            # print(f"{track_src} Smallest Paths: {smallest_paths}")
            cumulative_short_path[track_src] = {"shortest_paths": smallest_paths, "next_hops": next_hops}
            print(f"{track_src} Cumulative Short Path: {cumulative_short_path}")
        return cumulative_short_path

    def construct_routing_table(self, routing_info):
        routing_table = []
        routing = defaultdict(dict)
        for track_src, data in routing_info.items():
            for destination, distance in data["shortest_paths"].items():
                next_hop = data["next_hops"][destination]
                print(f"next hop {next_hop}")
                if distance == 9999 and next_hop == []:
                    next_hop = -1
                    distance = 9999
                elif distance == 0:
                    next_hop = track_src
                elif distance != 9999 and len(next_hop) == 1:
                    next_hop = destination
                else:
                    next_hop = next_hop[1]
                print(f"{track_src},{destination}:{next_hop},{distance}")
                if (self.switch_specs[track_src]["Status"] == True):
                    routing_table.append([track_src, destination, next_hop, distance])
                    routing[track_src][destination] = next_hop
                
        routing_table_update(routing_table)
        
        return routing
    
    def send(self, routing):
        for switch, route in routing.items():
            if self.switch_specs[switch]["Status"] == True:
                string = f"{switch}"
                for dest, next_hop in route.items():
                    string += f"\n{switch} {dest} {next_hop}"
                self.controller_socket.sendto(string.encode(), (self.switch_specs[switch]["Switch_HostName"], self.switch_specs[switch]["Switch_Port"]))
                
    def RegisterResponse(self, switch_ID, specs):
        switch_neighbours = self.adj_matrix[switch_ID]
        num_neighbours    = f"{len(switch_neighbours)}"
        print(num_neighbours)
        
        for neighbour in switch_neighbours:
            neighbour_hostname  = self.switch_specs[neighbour]["Switch_HostName"]
            neighbour_port      = self.switch_specs[neighbour]["Switch_Port"]
            num_neighbours     += f"\n{neighbour} {neighbour_hostname} {neighbour_port}"
            print(f"{neighbour} {neighbour_hostname} {neighbour_port}\n")    

        self.controller_socket.sendto(num_neighbours.encode(), (specs["Switch_HostName"], specs["Switch_Port"]))    
        register_response_sent(switch_ID)
        
    def ConnectSocket(self):
        print("Creating controller socket...\n")
        self.controller_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.controller_socket.bind(("localhost", self.controller_port))
        
        for i in range(self.num_switches):
            (data, switch_addr) = self.controller_socket.recvfrom(1024)
            switch_ID = int(data.decode("utf-8").split()[0])
            print(f"Register Request from switch {switch_ID} received.")
            self.counter[switch_ID] = time.time()
            self.switch_specs[switch_ID] = {"Switch_HostName": switch_addr[0], "Switch_Port": switch_addr[1], "Status": True}
            register_request_received(switch_ID)
        
        print("All requests registered successfully!\n")
        for switch_ID, specs in self.switch_specs.items():
            self.RegisterResponse(switch_ID, specs)
            
    def CreateSendRT(self):
        routing = self.construct_routing_table(self.path_computation())
        self.send(routing)
        
    def ControllerOperations(self):
        TIMEOUT = 6
        
        while True:
            create_flag = False
            (data, switch_addr) = self.controller_socket.recvfrom(1024)
            decoded_msg = data.decode('utf-8')
            if decoded_msg.split()[1] == "Register_Request":
                switch_ID = int(decoded_msg.split()[0])
                self.switch_specs[switch_ID] = {"Switch_HostName": switch_addr[0], 
                                                "Switch_Port":     switch_addr[1], 
                                                "Status":          True}
                register_request_received(switch_ID)
                self.RegisterResponse(switch_ID, self.switch_specs[switch_ID])
                create_flag = True
                print(f"Register Request from switch {switch_ID} received.") 
                print(f"Create Flag: {create_flag}")
            else: 
                switch_ID = int(decoded_msg.split("\n")[0])
                self.counter[switch_ID] = time.time()
                for neighbour_id, last_time in self.counter.items():
                    if time.time() - last_time > TIMEOUT and self.switch_specs[neighbour_id]["Status"] == True:
                        self.switch_specs[neighbour_id]["Status"] = False
                        topology_update_switch_dead(neighbour_id)
                        create_flag = True
                    elif time.time() - last_time <= TIMEOUT and self.switch_specs[neighbour_id]["Status"] == False:
                        self.switch_specs[neighbour_id]["Status"] = True
                        topology_update_switch_alive(neighbour_id)
                        create_flag = True
                n_stat = decoded_msg.split("\n")[1:]
                for n in n_stat:
                    if len(n.split()) == 2:
                        neighbour_id, status = n.split()
                        if self.adj_matrix[switch_ID][int(neighbour_id)]["Status"] != status and self.switch_specs[int(neighbour_id)]["Status"] == True:
                            # print(f"Mismatch: {status} not equals {self.adj_matrix[switch_ID][int(neighbour_id)]['Status']}")
                            print(f"Switch_ID: {switch_ID} Neighbour_ID: {neighbour_id} Status: {status}")
                            print
                            if status == "False":
                                topology_update_link_dead(switch_ID, int(neighbour_id))
                            self.adj_matrix[switch_ID][int(neighbour_id)]["Status"] = status
                            create_flag = True
            if create_flag == True:
                self.CreateSendRT()
                    
def main():
    num_args = len(sys.argv)
    if num_args < 3:
        print ("Usage: python controller.py <port> <config file>\n")
        sys.exit(1)

    controller_port, config_file = int(sys.argv[1]), sys.argv[2]
    num_switches, dij_graph      = process_config(config_file)
    controller                   = ControllerServer(controller_port, num_switches, dij_graph)  
    
    controller.ConnectSocket()
    routing = controller.construct_routing_table(controller.path_computation())
    controller.send(routing)
    
    controller.ControllerOperations()
if __name__ == "__main__":
    main()