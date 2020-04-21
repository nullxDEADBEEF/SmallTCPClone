import socket

# create UDP socket
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

# bind socket to port
server_address = ( "127.0.0.1", 10000 )
print( "starting ip on {} port {}".format( *server_address ) )
sock.bind( server_address )

QUIT_MESSAGE = b"QUIT"
ACCEPT_STRING_INDEX = 1


def handle_handshake():
    com_counter = 0
    client_message, client_address = sock.recvfrom( 4096 )
    # get the counter after we split the message with format "com-<com_counter>"
    # first split -> [com, 0 <ip address>] => second split => [0, <ip address>]
    # we then do index 0 to get counter
    message = client_message.decode().split( "-" )[0]
    client_counter = client_message.decode().split( "-" )[1].split( " " )[0]
    client_counter = int( client_counter )
    # check if we get a "com" message
    if message == "com" and com_counter == client_counter:
        sock.sendto( ( "com-{} accept ".format( com_counter ) + server_address[0] ).encode(), client_address )
    else:
        sock.sendto( "Error in handshake\nExpected: com\nGot: {}".format( message ).encode(), client_address )
        handle_handshake()
    data, client_address = sock.recvfrom( 4096 )
    data_list = data.split()
    if data_list[ACCEPT_STRING_INDEX].decode() == "accept":
        print( "Client accepted connection request" )
        com_counter += 1
    else:
        print( "Client didnt accept connection request" )
        handle_handshake()


def handle_client_message():
    msg_counter = 0
    res_counter = 1
    running = True
    while running:
        print( "\nwaiting to receive message" )
        data, client_address = sock.recvfrom( 4096 )
        message = data.decode().split( "-" )[0]
        # msg-0 = ada
        client_counter = data.decode().split( "-" )[1].split( " " )[0]
        client_counter = int( client_counter )

        print( "received {} bytes from {}".format( len( data ), client_address ) )

        if data:
            if data == QUIT_MESSAGE:
                running = False
            elif message == "msg" and msg_counter == client_counter:
                automated_message = "res-{} = {}".format( res_counter, "I am server" ).encode()
                sent = sock.sendto( automated_message, client_address )
                res_counter += 2
                msg_counter += 2
                print( "sent {} bytes back to {}".format( sent, client_address ) )
            else:
                sock.sendto( "Error in message\nExpected: msg, counter: {}\nGot: {}, counter: {}"
                             .format( msg_counter, message, client_counter ).encode(), client_address )
    print( "Closing socket..." )
    sock.close()


handle_handshake()
handle_client_message()
