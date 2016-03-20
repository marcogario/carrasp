import socket
import sys

IP_ADDR = "192.168.1.8"


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = (IP_ADDR, 8080)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

data = ""
while True:
    # Wait for a connection
    connection, client_address = sock.accept()
    try:
        print('Connection from %s' % str(client_address))
        while True:
            new_data = connection.recv(4096)
            if not new_data:
                print("Exiting..")
                break
            else:
                data += new_data
            print("received '%s'" % len(data))
            if '\n' in data:
                print(data)
                data = ""

    except KeyboardInterrupt:
        # Clean up the connection
        connection.close()
