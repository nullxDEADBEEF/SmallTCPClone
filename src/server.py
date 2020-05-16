import socket
import sys

# TODO: implement automation of package sending

# create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# bind socket to port
server_address = ("127.0.0.1", 10000)
print("starting ip on {} port {}".format(*server_address))
sock.bind(server_address)

ACCEPT_STRING_INDEX = 1
MAX_MESSAGE_SIZE = 4096
CONNECTION_TOLERANCE = 4.0
TERMINATE_CLIENT_PACKET = "con-res 0xFE"


# handle connection request from client
def handle_handshake():
    com_counter = 0
    try:
        client_message, client_address = sock.recvfrom(MAX_MESSAGE_SIZE)
        # get the counter after we split the message with format "com-<com_counter>"
        # first split -> [com, 0 <ip address>] => second split => [0, <ip address>]
        # we then do index 0 to get counter
        message_type = client_message.decode().split("-")[0]
        message = client_message.decode().split(" ")[1]
        # check if we get a "com" message
        if message_type == "com" and message == socket.gethostbyname(socket.gethostname()):
            sock.sendto(("com-{} accept ".format(com_counter) + server_address[0]).encode(), client_address)
        else:
            sock.sendto("Error in handshake\nExpected: com\nGot: {}".format(message_type).encode(), client_address)
            handle_handshake()
        data, client_address = sock.recvfrom(MAX_MESSAGE_SIZE)
        data_list = data.split()
        if data_list[ACCEPT_STRING_INDEX].decode() == "accept":
            print("Client accepted connection request")
            return client_address
        else:
            print("Client didnt accept connection request")
            handle_handshake()
    except KeyboardInterrupt:
        sys.exit()


def handle_client_message():
    client_address = handle_handshake()
    running = True
    while running:
        try:
            # start tolerance timer
            sock.settimeout(CONNECTION_TOLERANCE)

            print("\nwaiting to receive message")
            data, client_address = sock.recvfrom(MAX_MESSAGE_SIZE)

            if data.decode() == "con-h 0x00":
                print("con-h 0x00, Heartbeat received...")

            print("received {} bytes from {}".format(len(data), client_address))

            if data:
                if data.decode() == "con-res 0xFF":
                    print(data.decode())
                    print("Did not receive any packages for 4 seconds, shutting down...")
                    break

                message_type = data.decode().split("-")[0]
                # send a response if we got a message type of "msg"
                if message_type == "msg":
                    res_counter = int(data.decode().split("-")[1].split()[0])
                    res_counter += 1
                    automated_message = "res-{} = {}".format(res_counter, "I am server").encode()
                    sent = sock.sendto(automated_message, client_address)
                    print("sent {} bytes back to {}".format(sent, client_address))
                elif data.decode().split("-")[0] != "con" and data.decode().split("-")[0] != "com":
                    sock.sendto("Error in message".encode(), client_address)
        except KeyboardInterrupt:
            sys.exit()
        except socket.timeout:
            print("Sent terminating message")
            sock.sendto(TERMINATE_CLIENT_PACKET.encode(), client_address)
            data = sock.recv(MAX_MESSAGE_SIZE).decode("utf-8")
            print(data)
            break

    print("Closing socket...")
    sock.close()


if __name__ == "__main__":
    handle_client_message()
