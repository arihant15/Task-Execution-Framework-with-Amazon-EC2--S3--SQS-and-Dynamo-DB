import boto.sqs
import sys, os, base64
from boto.sqs.message import Message

conn = boto.sqs.connect_to_region(
    "us-west-2",
     aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
     aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))


# conn = boto.sqs.connect_to_region(
#     "us-west-2",
#     aws_access_key_id='AWS_ACCESS_KEY_ID',
#     aws_secret_access_key='AWS_SECRET_ACCESS_KEY')

print conn

my_queue = conn.get_queue('Task_to_Process')
m= my_queue.get_messages()
print len(m)
while (len(m)>0):
	print len(m)
	m= my_queue.get_messages()	
	my_queue.delete_message(m[0])
	
