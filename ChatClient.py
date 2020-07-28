import os
import sys
import socket
import threading
import time
import struct

def receive_msg():
    while True:
        msg = sock.recv(1024)
        if msg:
            print(msg.decode())
        else:
            sock.close()
            os._exit(0)

def ft_listener():
    while True:
        msg = ftpsock.recv(1024)
        if msg:
            msg = str(msg.decode())
            msgType = msg[0]
            msgContent = msg[1:]

            if msgType == 'r':
                #receive a file
                incoming_filename = msgContent
                receive_file_start(incoming_filename)
            elif msgType == 's':
                #send a file
                requested_filename = msgContent
                threading.Thread(target= send_file_start, args= (requested_filename, msgType)).start()
                
        else:
            sock.close()
            os._exit(0)

def receive_file_start(filename):
    recv_file_size_bytes=ftpsock.recv(4)
    if recv_file_size_bytes:
        recv_file_size= struct.unpack( '!L', recv_file_size_bytes[:4])[0]
        if recv_file_size:
            receive_file(filename,recv_file_size)
        else:
            print('File does not exist or is empty')
    else:
        print('File does not exist or is empty')

def receive_file(filename, recv_file_size):
    file = open(filename, 'wb')
    cur_size = 0
    while True:
        if cur_size >= recv_file_size:
            break
        recv_file_bytes = ftpsock.recv(1024)
        if recv_file_bytes:
            file.write(recv_file_bytes)
            cur_size = cur_size + 1024
        #else:
            #break
    file.close()

def send_file_start(filename, msgType):
    try:
        file_stat = os.stat(filename)
        if file_stat.st_size:
            file = open(filename, 'rb')
            send_file(file_stat.st_size, file)
        else:
            no_file(sock)
    except OSError:
        no_file(sock)

def send_file(file_size, file):
    send_file_size_bytes = struct.pack( '!L', file_size)
    ftpsock.send(send_file_size_bytes)
    while True:
        send_file_bytes = file.read(1024)
        if send_file_bytes:
            ftpsock.send(send_file_bytes)
        else:
            break
    file.close()

def no_file(ftpsock):
    zero_bytes = struct.pack( '!L', 0)
    ftpsock.send(zero_bytes)
    
serverport = ''
listenport = ''
argc = len( sys.argv )
for i in range(0,argc):
    if sys.argv[i] == '-l':
        listenport = int(sys.argv[i+1])
    elif sys.argv[i] == '-p':
        serverport = int(sys.argv[i+1])
server = 'localhost'
listenportstr = str(listenport)

servsock = socket.socket()
servsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servsock.bind(('localhost', listenport))
servsock.listen(5)

print('Enter your username')
username = sys.stdin.readline()
username = username.rstrip("\n")
hellomsg = listenportstr + username

sock = socket.socket()
sock.connect((server,serverport))

threading.Thread(target= receive_msg).start()

sock.send(hellomsg.encode())
ftpsock, addr = servsock.accept()
threading.Thread(target= ft_listener).start()

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
        sock.send(message.encode())

    elif option == 'f':
        print('Who owns the file?')
        fileowner = sys.stdin.readline().rstrip('\n')
        print('Which file do you want?')
        filename = sys.stdin.readline().rstrip('\n')
        request = option + filename
        reqMsg = request + '\n' + fileowner
        sock.send(reqMsg.encode())

    elif option == 'x':
        print('closing your sockets...goodbye')
        sock.close()
        os._exit(0)

