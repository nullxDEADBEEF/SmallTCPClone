import socket
import configparser
import threading
import time
import sys
import os

# config parser to load our client settings
config_parser = configparser.ConfigParser()

# load in settings
config_parser.read("opt.conf")
keep_alive = config_parser.getboolean("DEFAULT_SETTINGS", "KeepAlive")

# create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ("127.0.0.1", 10000)

ACCEPT_STRING_INDEX = 1
MAX_MESSAGE_SIZE = 4096
HEARTBEAT_TIMER = 3.0

ip = socket.gethostbyname(socket.gethostname())
msg_counter = 0


# sends heartbeat to server if flag is set
def send_heartbeat():
    heartbeat_message = "con-h 0x00"
    if keep_alive:
        while True:
            time.sleep(HEARTBEAT_TIMER)
            sock.sendto(heartbeat_message.encode(), server_address)


# initialize connection with a three-way handshake
def do_handshake():
    com_counter = 0
    print("com-{} ".format(com_counter) + ip)
    sock.sendto("com-{} {}".format(com_counter, ip).encode(), server_address)
    server_response, server = sock.recvfrom(MAX_MESSAGE_SIZE)
    server_response = server_response.decode()
    if server_response.split()[ACCEPT_STRING_INDEX] != "accept":
        print(server_response)
        sys.exit(0)
    else:
        print(server_response)
        client_accept = "com-{} accept".format(com_counter)
        sock.sendto(client_accept.encode(), server_address)
        if client_accept.split()[ACCEPT_STRING_INDEX] != "accept":
            print("You didnt accept the connection request")
            sys.exit(0)
        else:
            print(client_accept)


def send_message():
    while True:
        try:
            if config_parser.getboolean("DEFAULT_SETTINGS", "AutomateSending"):
                message = "Automated message"
                message = "msg-{} = {}".format(msg_counter, message)
                print(message)
                sock.sendto(message.encode(), server_address)
                time.sleep(0.1)
            else:
                # encode message into bytes
                message = input("> ")
                message = "msg-{} = {}".format(msg_counter, message)
                # send data
                print(message)
                sock.sendto(message.encode(), server_address)
                # we sleep shortly to let response be printed before we get input again
                time.sleep(0.1)
        except (KeyboardInterrupt, OSError):
            sys.exit()


def receive_response():
    global msg_counter
    while True:
        data, server = sock.recvfrom(MAX_MESSAGE_SIZE)
        # we received termination package, time to shutdown
        if data.decode() == "con-res 0xFE":
            sock.sendto("con-res 0xFF".encode(), server)
            sock.close()
            print("Idle for 4 seconds, shutting down...")
            os._exit(1)

        elif data.decode().split("-")[0] == "res":
            msg_counter = int(data.decode().split("-")[1].split()[0])
            msg_counter += 1
            print(data.decode())
        else:
            print(data.decode())
            sock.close()
            os._exit(1)


def try_to_bypass_handshake():
    sock.sendto("com-0 try_to_bypass".encode(), server_address)


def message_without_protocol_standard():
    sock.sendto("This msg doesnt follow protocol".encode(), server_address)


if __name__ == "__main__":
    # try_to_bypass_handshake()
    do_handshake()
    heartbeat_thread = threading.Thread(target = send_heartbeat)
    heartbeat_thread.setDaemon(True)
    heartbeat_thread.start()
    receive_thread = threading.Thread(target = receive_response)
    receive_thread.setDaemon(True)
    receive_thread.start()
    # message_without_protocol_standard()
    send_message()
