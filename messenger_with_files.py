import os
import sys
import socket
import threading
import struct

argc = len( sys.argv )
client = False
lport = 0000
sport = 0000
server = 'localhost'
clientserver = 'localhost'

for i in range(0,argc):
    if sys.argv[i] == '-l':
        lport = int(sys.argv[i+1])
    elif sys.argv[i] == '-p':
        sport = int(sys.argv[i+1])
        client = True
    elif sys.argv[i] == '-s':
        clientserver = sys.argv[i+1]


def client_connection(sendPort, serverAddr):
    #create client connection port
    csock = socket.socket()
    csock.connect((serverAddr,sendPort))

    #send listening port info to remote server
    lport_string = str(lport)
    csock.send(lport_string.encode())

    while True:
        print("Enter an option ('m', 'f', 'x'):")
        print('  (M)essage (send)')
        print('  (F)ile (request)')
        print(' e(X)it')

        option = sys.stdin.readline().strip('\n')
        if option == 'm':
            print('Enter your message:')
            message = sys.stdin.readline().rstrip('\n')
            message = option + message
            csock.send(message.encode())

        elif option == 'f':
            print('Which file do you want?')
            filename = sys.stdin.readline().rstrip('\n')
            request = option + filename
            csock.send(request.encode())
            recv_file_size_bytes=csock.recv(4)
            if recv_file_size_bytes:
                recv_file_size= struct.unpack( '!L', recv_file_size_bytes[:4])[0]
                if recv_file_size:
                    receive_file(csock,filename,recv_file_size)
                else:
                    print('File does not exist or is empty')
            else:
                print('File does not exist or is empty')

        elif option == 'x':
            print('closing your sockets...goodbye')
            csock.close()
            os._exit(0)

def receive_file(csock, filename, recv_file_size):
    file = open(filename, 'wb')
    cur_size = 0
    while True:
        if cur_size >= recv_file_size:
            break
        recv_file_bytes = csock.recv(1024)
        cur_size = cur_size + 1024
        if recv_file_bytes:
            file.write(recv_file_bytes)
        else:
            break
    file.close()

def send_file(sock, file_size, file):
    send_file_size_bytes = struct.pack( '!L', file_size)
    sock.send(send_file_size_bytes)
    while True:
        send_file_bytes = file.read(1024)
        if send_file_bytes:
            sock.send(send_file_bytes)
        else:
            break
    file.close()

def no_file(sock):
    zero_bytes = struct.pack( '!L', 0)
    sock.send(zero_bytes)

#create sending thread if client
if client:
    threading.Thread(target=client_connection, args=(sport,clientserver) ).start()

servsock = socket.socket()
servsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servsock.bind((server, lport))
servsock.listen(5)
sock, addr = servsock.accept()
servsock.close()

#wait for listening port msg from remote client
msg = sock.recv(1024)
sport = int(msg.decode())

#create sending thread if server
if not client:
    threading.Thread(target=client_connection, args=(sport,clientserver) ).start()

while True:
    msg = sock.recv(1024)
    if msg:
        msg = str(msg.decode())
        msgType = msg[0]
        msgContent = msg[1:]
        

        if msgType == 'm':
            print(msgContent)

        elif msgType == 'f':
            file_name = msgContent
            try:
                file_stat = os.stat(file_name)
                if file_stat.st_size:
                    file = open(file_name, 'rb')
                    send_file(sock, file_stat.st_size, file)
                else:
                    no_file(sock)
            except OSError:
                no_file(sock)
    else:
        sock.close()
        os._exit(0)
                


