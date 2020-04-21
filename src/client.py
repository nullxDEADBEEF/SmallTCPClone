import socket
import sys

# create UDP socket
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

server_address = ( "127.0.0.1", 10000 )

QUIT_MESSAGE = b"QUIT"
ACCEPT_STRING_INDEX = 1

msg_counter = 0
res_counter = 1
ip = socket.gethostbyname( socket.gethostname() )


def do_handshake():
    com_counter = 0
    print( "com-{} ".format( com_counter ) + ip )
    sock.sendto( "com-{} {}".format( com_counter, ip ).encode(), server_address )
    server_response, server = sock.recvfrom( 4096 )
    server_response = server_response.decode()
    if server_response.split()[ACCEPT_STRING_INDEX] != "accept":
        print( server_response )
        sys.exit()
    else:
        print( server_response )
        client_accept = "com-{} accept".format( com_counter )
        sock.sendto( client_accept.encode(), server_address )
        if client_accept.split()[ACCEPT_STRING_INDEX] != "accept":
            print( "You didnt accept the connection request" )
            sys.exit()
        else:
            print( client_accept )
            com_counter += 1


def send_message():
    global msg_counter
    # encode message into bytes
    message = input( "> " )
    message = "msg-{} = {}".format( msg_counter, message ).encode()
    # send data
    print( message.decode() )
    sock.sendto( message, server_address )
    msg_counter += 1
    return message


def receive_response():
    global msg_counter
    global res_counter
    data, server = sock.recvfrom( 4096 )
    print( data.decode() )
    msg_counter += 1
    res_counter += 2


def handle_messages():
    connected = True
    while connected:
        try:
            send = send_message()
            if send == QUIT_MESSAGE:
                connected = False
            else:
                receive_response()
        except OSError as ex:
            print( "Error: {}".format( ex ) )

    print( "closing socket" )
    sock.close()


do_handshake()
handle_messages()
