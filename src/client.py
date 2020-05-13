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
print(keep_alive)

# create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ("127.0.0.1", 10000)

QUIT_MESSAGE = b"QUIT"
QUIT_MESSAGE_INDEX = 1
ACCEPT_STRING_INDEX = 1
MAX_MESSAGE_SIZE = 4096
HEARTBEAT_TIMER = 3.0

msg_counter = 0
res_counter = 1
ip = socket.gethostbyname(socket.gethostname())


def send_heartbeat():
    heartbeat_message = "con-h 0x00"
    if keep_alive:
        while True:
            time.sleep(HEARTBEAT_TIMER)
            sock.sendto(heartbeat_message.encode(), server_address)


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
            com_counter += 1


def send_message():
    global msg_counter
    while True:
        try:
            # encode message into bytes
            message = input("> ")
            message = "msg-{} = {}".format(msg_counter, message).encode()
            # send data
            print(message.decode())
            sock.sendto(message, server_address)
            if message.decode().split("= ")[QUIT_MESSAGE_INDEX] == QUIT_MESSAGE.decode():
                sys.exit()
            msg_counter += 1
            # we sleep shortly to let response be printed before we get input again
            time.sleep(0.1)
        except KeyboardInterrupt as ex:
            print(ex)


def receive_response():
    global msg_counter
    global res_counter
    while True:
        data, server = sock.recvfrom(MAX_MESSAGE_SIZE)
        if data.decode() == "con-res 0xFE":
            sock.sendto( "con-res 0xFF".encode(), server)
            sock.close()
            print("Idle for 4 seconds, shutting down...")
            os._exit(1)

        if data.decode().split("-")[0] != "res":
            print("Server couldnt match msg counter with yours...\nExiting...")
            sock.close()
            sys.exit()
        else:
            print(data.decode())
            msg_counter += 1
            res_counter += 2


if __name__ == "__main__":
    do_handshake()
    heartbeat_thread = threading.Thread(target = send_heartbeat)
    heartbeat_thread.setDaemon(True)
    heartbeat_thread.start()
    receive_thread = threading.Thread(target = receive_response)
    receive_thread.setDaemon(True)
    receive_thread.start()
    send_message()


