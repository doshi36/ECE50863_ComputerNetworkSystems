#!/usr/bin/env python3

import socket

PORT = 3000
IP_ADDR = '127.0.0.1'

if __name__ == "__main__":

    print("Creating socket")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # not SOCK_STREAM, which is for TCP. We want UDP, which requires SOCK_DGRAM

    print(f"Socket address before binding is {server_socket.getsockname()}. The format is (ip_addr, socket #)") 
    print("You can't send data to port 0 (the OS will kill your program, since that port is reserved) so we need to change the ports in order for people")
    print("to be able to send us data. That's done by 'binding' the socket to a new port")

    print(f"Binding socket to ip_addr {IP_ADDR} and port {PORT}")
    server_socket.bind((IP_ADDR, PORT))

    print(f"We've now bound the socket to {server_socket.getsockname()}, so we can now send messages to the server by specifying its address in sendto")

    print(f"Waiting on client to send us a message")
    (data, client_addr) = server_socket.recvfrom(1024) # Client address really is a tuple of (ip_addr, port number) from the sender

    print(f"Recieved message from client")
    print(f"Client address is {client_addr}")
    print(f"Client data is '{data.decode('utf-8')}'")

    print(f"Sending message 'thank you' back to client")

    # Note that we're using sendto and recvfrom for both the client and server examples. These functions don't require a connection (ie. they work with UDP) and are the recommended
    # way to communicate over UDP. Some of the other functions for sockets only work with TCP, but it's not obvious which those are unless you read the
    # documentation, which is a good idea but also somewhat annoying. So we would recommend sticking to these functions.
    server_socket.sendto("thank you".encode('UTF-8'), client_addr)


    