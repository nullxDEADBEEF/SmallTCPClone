import socket
import sys

# create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ("127.0.0.1", 10000)

QUIT_MESSAGE = b"QUIT"
QUIT_MESSAGE_INDEX = 1
ACCEPT_STRING_INDEX = 1
MAX_MESSAGE_SIZE = 4096

msg_counter = 0
res_counter = 1
ip = socket.gethostbyname(socket.gethostname())


def do_handshake():
    com_counter = 0
    print("com-{} ".format(com_counter) + ip)
    sock.sendto("com-{} {}".format(com_counter, ip).encode(), server_address)
    server_response, server = sock.recvfrom(MAX_MESSAGE_SIZE)
    server_response = server_response.decode()
    if server_response.split()[ACCEPT_STRING_INDEX] != "accept":
        print(server_response)
        sys.exit()
    else:
        print(server_response)
        client_accept = "com-{} accept".format(com_counter)
        sock.sendto(client_accept.encode(), server_address)
        if client_accept.split()[ACCEPT_STRING_INDEX] != "accept":
            print("You didnt accept the connection request")
            sys.exit()
        else:
            print(client_accept)
            com_counter += 1


def send_message():
    global msg_counter
    # encode message into bytes
    message = input("> ")
    message = "msg-{} = {}".format(msg_counter, message).encode()
    # send data
    print(message.decode())
    sock.sendto(message, server_address)
    msg_counter += 1
    return message


def receive_response():
    global msg_counter
    global res_counter
    data, server = sock.recvfrom(MAX_MESSAGE_SIZE)
    if data.decode() == "con-res 0xFE":
        print(data.decode())
        sock.sendto( "con-res 0xFF".encode(), server)
        return False
    elif data.decode().split("-")[0] != "res":
        print("Server couldnt match msg counter with yours...\nExiting...")
        return False
    else:
        print(data.decode())
        msg_counter += 1
        res_counter += 2
        return True


def handle_messages():
    connected = True
    while connected:
        try:
            send = send_message()
            if send.decode().split("= ")[QUIT_MESSAGE_INDEX] != QUIT_MESSAGE.decode():
                got_response = receive_response()
                if not got_response:
                    break
            else:
                break
        except OSError as ex:
            print("Error: {}".format(ex))

    print("closing socket")
    sock.close()


do_handshake()
handle_messages()
