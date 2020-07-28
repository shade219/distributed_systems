#! python

#EchoClient

def usage( script_name ):
    print( 'Usage: py ' + script_name + ' <port number>' )

if __name__ == "__main__":
	# get the command line arguments
	import sys
	import socket
	argc= len( sys.argv )
	if argc != 2:
		usage( sys.argv[0] )
		sys.exit()	
	message= sys.stdin.readline() # read a message from standard input
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP/IP socket
	sock.connect(('localhost', int(sys.argv[1])))
	sock.send( message.encode() )
	return_msg= sock.recv( 1024 )
	if return_msg:
		print( 'message returned: ' + return_msg.decode() )
	else:
		print( 'other side shut down' )
	sock.close()
