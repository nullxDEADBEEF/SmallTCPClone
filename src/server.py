import socket

# create UDP socket
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

# bind socket to port
server_address = ( 'localhost', 10000 )
print( 'starting ip on {} port {}'.format( *server_address ) )
sock.bind( server_address )

while True:
    print( '\nwaiting to receive message' )
    data, address = sock.recvfrom( 4096 )

    print( 'received {} bytes from {}'.format( len( data ), address ) )

    if data:
        automated_message = b'I am server'
        sent = sock.sendto( automated_message, address )
        print( 'sent {} bytes back to {}'.format( sent, address ) )




