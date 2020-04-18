import socket
import sys

# TODO: update msg-counter


# create UDP socket
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

server_address = ( "127.0.0.1", 10000 )

QUIT_MESSAGE = b"QUIT"

msg_counter = 0
ip = socket.gethostbyname( socket.gethostname() )


def do_handshake():
    com_counter = 0
    print( "> com-{} ".format( com_counter ) + ip )

    sock.sendto( ip.encode(), server_address )
    server_acceptance, server = sock.recvfrom( 4096 )
    print( server_acceptance.decode() )
    client_accept = input().encode()
    sock.sendto( client_accept, server_address )
    if client_accept != "accept".encode():
        print( "You didnt accept the connection" )
        print( "Shutting down...." )
        sys.exit( 0 )
    com_counter += 1


def send_message():
    # encode message into bytes
    message = input( "> " ).encode()
    # send data
    print( "msg-{} = {}".format( msg_counter, message.decode() ) )
    sock.sendto( message, server_address )
    return message


def receive_response():
    data, server = sock.recvfrom( 4096 )
    print( "res-{} = {}".format( msg_counter, data.decode() ) )


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
