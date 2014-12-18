import sys
import os
import json
import time
from thread import *
import boto.dynamodb
import boto.sqs
from boto.sqs.message import Message
import boto.s3.connection
from boto.s3.key import Key

conn = boto.sqs.connect_to_region(
    "us-west-2",
     aws_access_key_id='AWS_ACCESS_KEY_ID',
    aws_secret_access_key='AWS_SECRET_ACCESS_KEY')

conn_dynamo = boto.dynamodb.connect_to_region(
    "us-west-2",
     aws_access_key_id='AWS_ACCESS_KEY_ID',
    aws_secret_access_key='AWS_SECRET_ACCESS_KEY')

conn_s3 = boto.connect_s3(
     aws_access_key_id='AWS_ACCESS_KEY_ID',
    aws_secret_access_key='AWS_SECRET_ACCESS_KEY')
    is_secure=False,
    calling_format = boto.s3.connection.OrdinaryCallingFormat(),)

task_queue = conn.get_queue('Task_to_Process')
processed_queue = conn.get_queue('Processed_Task')
table = conn_dynamo.get_table('Task_Monitor')
try:
    bucket = conn_s3.create_bucket('video-hub')
    print 'S3 Bucket Created ...'
except Exception as e:
    print 'S3 Bucket Already Created ...'
threadCount = 0
threadLimit = 16
imageCount = 0
taskLimit = 60

def responseMessage(clientID, jobID, task):
   a = {}
   a["clientID"] = clientID
   a["jobID"] = jobID
   a["task"] = task
   j = json.dumps(a)
   return j

def taskProcess(msg, jObj):
    try:
        exe = 'wget ' + str(jObj["task"])
        os.system(exe)
        print 'Image Downloaded Successful...'
    except Exception as e:
        m = Message()
        m.set_body(jObj)
        task_queue.write(m)
        key = jObj["clientID"]+";"+jObj["jobID"]
        item = table.get_item(hash_key = key)
        item['Body'] = 'False'
        item.put()
        print 'Interrupted' + str(e)
    '''
    global threadCount,imageCount
    threadCount = threadCount - 1
    #imageCount = imageCount + 1
    '''

def imageProcess(cID, jID):
    try:
        os.system("./image.sh")
        file_name = str(cID) + str(jID) +".mpg"
        tempcommand = 'mv output.mpg ' + file_name
        os.system(tempcommand)
        print 'Uploading File'
        k = Key(bucket)
        k.Key = file_name
        k.set_contents_from_filename(file_name)
        k.set_canned_acl('public-read')
        url = k.generate_url(0, query_auth=False, force_http=True)
        print url
        m1 = Message()
        j = responseMessage(cID, jID, url)
        m1.set_body(j)
        processed_queue.write(m1)
        tempcommand = 'rm -rf ' + file_name
        os.system(tempcommand)
        global  imageCount
        imageCount = 0
    except Exception as e:
        print 'Interrupted' + str(e)
        imageCount = 0

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
        if imageCount == taskLimit:
            imageProcess(jString["clientID"], jString["jobID"])
            #imageCount = 90
        if imageCount < taskLimit:
            #if threadCount < threadLimit:
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
                taskProcess(m[0], jString)
                #threadCount = threadCount + 1
                imageCount = imageCount + 1
            else:
                print 'Duplicate Job => Client ID : ' + jString["clientID"] + ", Job ID : " + jString["jobID"]

    except Exception as e:
        e = 0

__author__ = 'arihant'
