import sys
import json
import time
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
table = conn_dynamo.get_table('Task_Monitor')
threadCount = 1
threadLimit = 16

def responseMessage(clientID, jobID, task):
   a = {}
   a["clientID"] = clientID
   a["jobID"] = jobID
   a["task"] = task
   j = json.dumps(a)
   return j

def taskProcess(msg, jObj):
    print jObj["task"]
    job = jObj["task"].split(' ')
    try:
        exe = 'time.'+job[0]+'('+str(float(job[1])/1000)+')'
        print 'Executing ... ' + exe
        exec (exe)
        print 'successful'
        m1 = Message()
        j = responseMessage(jObj["clientID"], jObj["jobID"], "1")
        m1.set_body(j)
        processed_queue.write(m1)
    except Exception as e:
        m = Message()
        m.set_body(jObj)
        task_queue.write(m)
        key = jObj["clientID"]+";"+jObj["jobID"]
        item = table.get_item(hash_key = key)
        item['Body'] = 'False'
        item.put()
        print 'Interrupted' + str(e)

    global threadCount
    threadCount = threadCount - 1

def checkStatus(job_id):
    try:
        item = table.get_item(hash_key = job_id)
        print 'job present .. Returning status : ' + item['Body']
        return item['Body']
    except Exception:
        print 'No job ... Returning False'
        return 'False'

while True:
    try:
        if threadCount <= threadLimit:
            m = task_queue.get_messages()
            msg = m[0].get_body()
            jString = json.loads(msg)
            task_queue.delete_message(m[0])
            #Check Dynamo DB
            key = str(jString["clientID"]) + ";" + str(jString["jobID"])
            print key
            print 'Checking Status'
            status = checkStatus(key)
            print 'Status : ' + status
            if status == 'False':
                item_data = {'Body': 'True'}
                item = table.new_item(hash_key = key, attrs = item_data)
                item.put()
                start_new_thread(taskProcess ,(m[0], jString, ))
                threadCount = threadCount + 1
            else:
                print 'Duplicate Job => Client ID : ' + jString["clientID"] + ", Job ID : " + jString["jobID"]
    except Exception as e:
        e = 0

__author__ = 'arihant'
