import socket
import time
from datetime import datetime
import configparser
import sys


# config parser to load our server settings
config_parser = configparser.ConfigParser()

# load settings
config_parser.read("opt.conf")
max_packets = config_parser.getint("DEFAULT_SETTINGS", "MaxPackages")

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
res_counter = 0


# handle connection request from client
def handle_handshake():
    com_counter = 0
    try:
        client_message, client_address = sock.recvfrom(MAX_MESSAGE_SIZE)
        log_message(client_message)
        # get the counter after we split the message with format "com-<com_counter>"
        # first split -> [com, 0 <ip address>] => second split => [0, <ip address>]
        # we then do index 0 to get counter
        message_type = client_message.decode().split(" ")[0]
        message = client_message.decode().split(" ")[1]
        # check if we get a "com" message and that we got a valid IP-address
        if message_type == "com-0" and socket.inet_aton(message):
            sock.sendto(("com-{} accept ".format(com_counter) + server_address[0]).encode(), client_address)
            log_message("com-{} accept ".format(com_counter) + server_address[0])
        else:
            sock.sendto("Error in handshake\nExpected: com-0\nGot: {}".format(message_type).encode(), client_address)
            log_message("Error in handshake\nExpected: com-0\nGot: {}".format(message_type))
            print("Error in handshake\nExpected: com-0\nGot: {}\nShutting down...".format(message_type))
            sys.exit()
        data, client_address = sock.recvfrom(MAX_MESSAGE_SIZE)
        data_list = data.split()

        if data_list[0].decode().startswith("com-") and data_list[ACCEPT_STRING_INDEX].decode() == "accept":
            log_message(data_list[ACCEPT_STRING_INDEX].decode())
            print("Client accepted connection request")
            return client_address
        else:
            log_message(data_list[ACCEPT_STRING_INDEX].decode())
            print("Client didnt accept connection request")
            sys.exit()
    except KeyboardInterrupt:
        sys.exit()
    except OSError as ex:
        print(ex)
        log_message("Error in handshake")
        sock.sendto("Error in handshake".encode(), client_address)
        sys.exit()


def handle_client_message():
    global res_counter
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

            if data and data.decode() != "con-h 0x00":
                message_type = data.decode()

                client_counter = int(data.decode().split("-")[1].split()[0])
                # send a response if we got a message type of "msg"
                if message_type.startswith("msg-") and res_counter == client_counter - 1 or\
                        client_counter == 0 and message_type.startswith("msg-"):
                    res_counter = client_counter + 1
                    # res_counter += 1
                    automated_message = "res-{} = {}".format(res_counter, "I am server").encode()
                    sent = sock.sendto(automated_message, client_address)
                    print("sent {} bytes back to {}".format(sent, client_address))
                elif data.decode().split("-")[0] != "con" and data.decode().split("-")[0] != "com":
                    sock.sendto("Error in message".encode(), client_address)
                    sys.exit()

        except KeyboardInterrupt:
            sys.exit()
        except socket.timeout:
            print("Sent terminating message")
            sock.sendto(TERMINATE_CLIENT_PACKET.encode(), client_address)
            data = sock.recv(MAX_MESSAGE_SIZE).decode("utf-8")
            if data == "con-res 0xFF":
                print("Received: " + data)
                print("Did not receive any packages for 4 seconds, shutting down...")
            break
        # we sleep the thread 1 sec divided by specified max packets
        # to avoid hitting over max packets per second
        time.sleep(1 / max_packets)

    print("Closing socket...")
    sock.close()


def log_message(message):
    log_file = open("log_messages.log", "a")
    log_file.write(f"[{datetime.now()}] {message}\n")
    log_file.close()


if __name__ == "__main__":
    handle_client_message()
