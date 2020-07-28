import os
import sys
import socket
import threading
import time
import struct

def receive_msg(clientsock, addr, username):
    while True:
        msgdata = clientsock.recv(1024)
        if msgdata:
            msg = msgdata.decode()
            msgType = msg[0]
            msgContent = msg[1:]

            if msgType == 'm':
                msg = username + ': ' + msgContent
                for clienttuple in client_list:
                    if clienttuple[2] != username:
                        clienttuple[0].send(msg.encode())
            #print(msg.decode(), end='')

            elif msgType == 'f':
                contentArray = msgContent.split('\n')
                #print('file requested')
                file_name = contentArray[0]
                #print('filename is ' + file_name)
                fileowner = contentArray[1]
                #print('fileowner is ' + fileowner)
                threading.Thread(target= relay_file, args= (fileowner, username, file_name)).start()
          
        else:
            client_list.remove((clientsock, addr, username))
            clientsock.close()
            sys.exit(0)

def relay_file(fileowner,requester,filename):
    #print('starting relay_file')
    for clienttuple in client_ftp_list:
        if clienttuple[1] == requester:
            requestersock = clienttuple[0]
        if clienttuple[1] == fileowner:
            ownersock = clienttuple[0]
    reqmsg = 'r' + filename
    ownmsg = 's' + filename
    requestersock.send(reqmsg.encode())
    ownersock.send(ownmsg.encode())
    recv_file_size_bytes=ownersock.recv(4)
    if recv_file_size_bytes:
        recv_file_size= struct.unpack( '!L', recv_file_size_bytes[:4])[0]
        requestersock.send(recv_file_size_bytes)
        currentsize = 0
        while currentsize <= recv_file_size:
            packet = ownersock.recv(1024)
            requestersock.send(packet)
            currentsize = currentsize + 1024
    
    

argc = len( sys.argv )
port = int(sys.argv[1])
server = 'localhost'
client_list = []
client_ftp_list = []

        
servsock = socket.socket()
servsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servsock.bind(('localhost', port))
servsock.listen(5)

while True:
    username = ''
    sock, addr = servsock.accept()
    hellomsg = sock.recv(1024)
    hellomsg = hellomsg.decode()
    clientport = int(hellomsg[0:4])
    username = hellomsg[4:]
    csock = socket.socket()
    csock.connect(('localhost',clientport))
    client_list.append((sock, addr, username))
    client_ftp_list.append((csock,username))
    threading.Thread(target= receive_msg, args= (sock, addr, username)).start()

servsock.close()
os._exit(0)

"""
message = sys.stdin.readline()
while message:
    sock.send(message.encode())
    message = sys.stdin.readline()

sock.close()
os._exit(0)
"""
