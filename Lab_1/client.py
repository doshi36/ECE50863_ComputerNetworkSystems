#!/usr/bin/env python3

import socket

if __name__ == "__main__":

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    msg = "Hello there".encode(encoding='UTF-8')

    # This is the server address, which we hard coded in server.py
    addr = ("127.0.0.1", 3000)

    # Before sending the socket is unbound, and hence has no ability to receieve data
    print(f"Before sending data the socket address is {client_socket.getsockname()}")

    client_socket.sendto(msg, addr)

    print(f"After sending the socket is automatically bound to a free port by the OS, allowing it to recieve data")
    print(f"The socket is now bound to {client_socket.getsockname()}")
    print(f"Recieving data from client")
    (data, server_addr) = client_socket.recvfrom(1024)

    print(f"Server data is '{data.decode('utf-8')}'")
