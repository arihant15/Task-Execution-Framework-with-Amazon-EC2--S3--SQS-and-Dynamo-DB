#!/usr/bin/python

import socket
import Queue
import sys
import json
import time
from thread import *
import threading

flag = 0
task_queue = Queue.Queue()
processed_queue = Queue.Queue()
threadCount = 1
threadLimit = 1
s = socket.socket()
host = socket.gethostname()
port = 55555
print "Socket Created ..."
s.bind((host, port))
print "Socket Bind Completed"
s.listen(5)
print "Socket now listening..."
print 'Listening for Connection ... '

class processThread(threading.Thread):
   def __init__(self, data):
      threading.Thread.__init__(self)
      self.data = data

   def run(self):
      global flag
      for i in self.data:
         job = i.split(' ')
         try:
            exe = 'time.'+job[0]+'('+str(float(job[1])/1000)+')'
            print 'Executing ... ' + exe
            exec (exe)
            flag = 1
         except Exception as e:
            print e
            flag = 0

def createMessage(clientID, jobID, task):
   a = {}
   a["clientID"] = clientID
   a["jobID"] = jobID
   a["task"] = task
   j = json.dumps(a)
   return j

def localWorkerThread(c, addr):
   c.sendall(str(addr))
   data = ''
   for i in range(0,9,1):
     data += c.recv(1024000)
   print(data)
   print len(data)
   data.strip()
   task = data.split('\n')
   task = task[:-1]
   task_count = len(task)
   job_id = 1
   global threadCount
   global threadLimit
   print 'Task Count : ' + str(task_count)
   print 'Writing Task to Queue ... '
   batch = 0
   threads = []
   while batch < task_count:
      for i in range(threadLimit):
         print batch
         thread = processThread(task[batch:(batch+(len(task)/threadLimit))])
         threads.append(thread)
         batch = batch + (len(task)/threadLimit)
   for th in threads:
      th.start()
   for th in threads:
      th.join()
   if flag == 1:
      print 'Sending Response to Client'
      reply = 'Status : Success'
      c.sendall(reply)
   else:
      print 'Sending Response to Client'
      reply = 'Status : Fail'
      c.sendall(reply)
   c.close()
   print 'Closing Scheduler connection for the Client ID : ' + str(addr)



while True:
   c, addr = s.accept()
   print 'Got connection from', addr
   start_new_thread(localWorkerThread, (c,addr[1], ))
c.close()

__author__ = 'arihant'
