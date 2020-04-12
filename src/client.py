import socket

# create UDP socket
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

server_address = ( 'localhost', 10000 )

QUIT_MESSAGE = b"QUIT"

com_counter = 0
msg_counter = 0

def handle_handshake():
    print( b"com-0 " )
    ip = input().encode()
    sock.sendto( ip, server_address )


def send_message():
    # encode message into bytes
    message = input( "> " ).encode()
    # send data
    print( "sending {!r}".format( message ) )
    sock.sendto( message, server_address )
    return message


def receive_response():
    print( "waiting to receive" )
    data, server = sock.recvfrom( 4096 )
    print( "received {!r}".format( data ) )


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
            print( "Error: {}", ex )

    print( 'closing socket' )
    sock.close()


handle_handshake()
handle_messages()
