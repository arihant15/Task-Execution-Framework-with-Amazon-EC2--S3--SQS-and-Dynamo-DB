#!/usr/bin/python           # This is client.py file

import socket               # Import socket module
import sys
from thread import *
from datetime import datetime

send = 'none'
task = 0
def clientThread(task_id, data):
    st = datetime.now()
    s = socket.socket()
    host = socket.gethostname()
    port = 55555
    s.connect((host, port))
    length = len(data)
    print length
    if length >= 8000:
        batch = length/80
        for i in range(0,(length),batch):
            print batch
            print i
            print ((i+batch)-1)
            s.sendall(str(data[i:((i+batch)-1)]))
            s.sendall('\n')
    else:
        batch = 0
        s.sendall(data)
    clientID = s.recv(1024000)
    print '\nClient ID : ' + str(clientID)
    flag = 1
    output = []
    while flag:
        response = s.recv(1024000)
        if response != None:
            output = response.split(',')
            print '\nResposne => Client ID : ' + str(clientID)
            for res in output:
                print res
            flag = 0
    s.close()
    print '\nConnection Closed for Job ID ' + str(task_id)
    et = datetime.now()
    print"Time Taken for Client ID "+ str(clientID) +" is : "+str(et-st)+" "

while send != 'q':
    send = raw_input('Enter the File Containing the Tasks or Press (q) to quit...\n')
    if send != 'q':
        file = open(send, 'rb')
        data = file.read()
        file.close()
        task = task + 1
        start_new_thread(clientThread ,(task, data, ))

__author__ = 'arihant'