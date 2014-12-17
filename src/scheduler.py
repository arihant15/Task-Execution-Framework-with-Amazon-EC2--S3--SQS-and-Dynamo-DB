#!/usr/bin/python

import socket
import sys
import time
import json
from thread import *
import boto.dynamodb
import boto.sqs
from boto.sqs.message import Message

conn = boto.sqs.connect_to_region(
    "us-west-2",
     aws_access_key_id='AKIAJHZT57DMEKJR3YMA',
    aws_secret_access_key='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')

conn_dynamo = boto.dynamodb.connect_to_region(
    "us-west-2",
   aws_access_key_id='AKIAJHZT57DMEKJR3YMA',
    aws_secret_access_key='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')

task_queue = conn.get_queue('Task_to_Process')
processed_queue = conn.get_queue('Processed_Task')
task_count = 0
task_type = 's'
try:
   s = socket.socket()
   host = socket.gethostname()
   port = 55555
   print "Socket Created ..."
   s.bind((host, port))
   print "Socket Bind Completed"
   s.listen(5)
   print "Socket now listening..."
except Exception as e:
   print e
try:
   task_table_schema = conn_dynamo.create_schema(
      hash_key_name='Job_ID',
      hash_key_proto_value=str
   )
   table = conn_dynamo.create_table(
      name = 'Task_Monitor',
      schema = task_table_schema,
      read_units = 10,
      write_units = 10
   )
   print 'Dynamo DB Table Created ... '
except Exception as e:
   print 'Dynamo DB Already Created ... '
print 'Listening for Connection ... '

def createMessage(clientID, jobID, task):
   a = {}
   a["clientID"] = clientID
   a["jobID"] = jobID
   a["task"] = task
   j = json.dumps(a)
   return j

def schedulerThread(c, addr):
   c.sendall(str(addr))
   data = c.recv(1024000)
   data.strip()
   task = data.split('\n')
   task = task[:-1]
   global task_count,task_type
   task_count = len(task)
   if task[0].find('jpg') >= 0:
      task_type = 'a'
      print task_type
   job_id = 1
   m = Message()
   print 'Task Count : ' + str(task_count)
   print 'Writing Task to Queue ... '
   for i in task:
      j = createMessage(addr, job_id, i)
      m.set_body(j)
      task_queue.write(m)
      job_id = job_id + 1
   print 'Writing Task to Queue Successful'

def responseThread(c, addr):
   print '\nReading Response from Queue ... '
   count = 0
   output = []
   global task_count,task_type
   while True:
      try:
         m1 = processed_queue.get_messages()
         msg = m1[0].get_body()
         jString = json.loads(msg)
         if jString["clientID"] == addr:
            processed_queue.delete_message(m1[0])
            print 'Deleted response from queue'
            if task_type == 'a':
               output.append(str(jString["task"]))
               print output
            count += 1

         if task_type == 's':
            if count == task_count:
               print 'Sending Response to Client'
               output.append('Status : Success')
               c.sendall(str(output))
               break

         if task_type == 'a':
            if count == (task_count)/60:
               print 'Sending Response to Client'
               reply = 'URL to Animoto : ...'
               c.sendall(str(output))
               break

      except Exception as e:
         e = None
         exec ('time.sleep(1)')
   c.close()
   print 'Closing Scheduler connection for the Client ID : ' + str(jString["clientID"])

while True:
   c, addr = s.accept()
   print 'Got connection from', addr
   start_new_thread(schedulerThread ,(c,addr[1], ))
   start_new_thread(responseThread ,(c,addr[1], ))
c.close()

__author__ = 'arihant'
