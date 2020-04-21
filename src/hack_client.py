import socket
import sys

############################# THIS IS USED TO HACK THE CLIENT AND TRY TO BYPASS PROTOCOL #######################


# create UDP socket
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

server_address = ( "127.0.0.1", 10000 )

QUIT_MESSAGE = b"QUIT"
ACCEPT_STRING_INDEX = 1

msg_counter = 0
ip = socket.gethostbyname( socket.gethostname() )


def do_handshake():
    com_counter = 0
    print( "com-{} ".format( com_counter ) + ip )

    sock.sendto( "com-{} {}".format( com_counter, ip ).encode(), server_address )
    server_response, server = sock.recvfrom( 4096 )
    print( server_response.decode() )
    client_accept = "com-{} accept".format( com_counter )
    sock.sendto( client_accept.encode(), server_address )
    if client_accept.split()[ACCEPT_STRING_INDEX] != "accept":
        print( "You didnt accept the connection request" )
        sys.exit()
    else:
        print( client_accept )
        com_counter += 1


# TODO: sent message again if msg-counter doesnt match on the server???
def send_message():
    global msg_counter
    # encode message into bytes
    message = input( "> " ).encode()
    # send data
    print( "msg-{} = {}".format( msg_counter, message.decode() ) )
    sock.sendto( message, server_address )
    msg_counter += 1
    return message


def receive_response():
    global msg_counter
    data, server = sock.recvfrom( 4096 )
    print( "res-{} = {}".format( msg_counter, data.decode() ) )
    msg_counter += 1


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
