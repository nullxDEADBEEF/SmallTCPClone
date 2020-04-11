import socket

# create UDP socket
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

server_address = ( 'localhost', 10000 )

QUIT_MESSAGE = b"QUIT"

connected = True
while connected:
    try:
        # encode the message into bytes
        message = input( "> " ).encode()
        # send data
        print( 'sending {!r}'.format( message ) )
        sent = sock.sendto( message, server_address )
        if message == QUIT_MESSAGE:
            connected = False
        else:
            # receive response
            print( 'waiting to receive' )
            data, server = sock.recvfrom( 4096 )
            print( 'received {!r}'.format( data ) )
    except OSError:
        print( "Error with the socket" )

print( 'closing socket')
sock.close()