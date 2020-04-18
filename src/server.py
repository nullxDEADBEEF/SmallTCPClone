import socket

# create UDP socket
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

# bind socket to port
server_address = ( "127.0.0.1", 10000 )
print( "starting ip on {} port {}".format( *server_address ) )
sock.bind( server_address )

QUIT_MESSAGE = b"QUIT"
client_connected = False


def handle_handshake():
    client_ip, address = sock.recvfrom( 4096 )
    # TODO  : replace with com counter
    sock.sendto( ( "> com-0 accept " + server_address[0] ).encode(), address )
    data, address = sock.recvfrom( 4096 )
    if data.decode() == "accept":
        print( "Client accepted connection request" )
    else:
        print( "Client didnt accept connection request" )
        handle_handshake()


def handle_client_message():
    running = True
    while running:
        print( "\nwaiting to receive message" )
        data, address = sock.recvfrom( 4096 )

        print( "received {} bytes from {}".format( len( data ), address ) )

        if data:
            if data == QUIT_MESSAGE:
                running = False
            else:
                automated_message = b'I am server'
                sent = sock.sendto( automated_message, address )
                print( "sent {} bytes back to {}".format( sent, address ) )
    print( "Closing socket..." )
    sock.close()


handle_handshake()
handle_client_message()
