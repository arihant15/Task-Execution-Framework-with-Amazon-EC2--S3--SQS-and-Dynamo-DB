import sys, os, base64
import boto.ec2
import boto.sqs
import time
import datetime

conn = boto.ec2.connect_to_region(
    "us-west-2",
     aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
     aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

qConn = boto.sqs.connect_to_region(
    "us-west-2",
     aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
     aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))



def createInstance():
	conn.run_instances(
        'AMI',
        key_name='KEY_NAME',
        instance_type='Instance_Type',
        security_groups=['Network_Group'])
	print "Instance created"

def createSpotInstance():
	req = conn.request_spot_instances(price='0.010',instance_type='Intance_Type',image_id='AMI',
	availability_zone_group='us-west-2')
	job_instance_id = None
	startTime=datetime.datetime.now()
	while job_instance_id == None:
		print "Check instance state"
		job_sir_id = req[0].id 
		reqs = conn.get_all_spot_instance_requests()
		print reqs
		for sir in reqs:
			if sir.id == job_sir_id:
				job_instance_id = sir.instance_id
				print "Instance Id " + str(job_instance_id)
				if(job_instance_id!=None):
					endTime=datetime.datetime.now()
					print "timetaken to boot"
					print endTime-startTime
				break
				time.sleep(300)

flag=True;
while(flag==True):
	my_queue = qConn.get_queue('Task_to_Process')
	#my_queue = qConn.get_queue('process')
	m= my_queue.get_messages()
	print "No of element in queue";
	size=my_queue.count()
	print size
	print "approx"
	if(size<1):
		print "Queue Empty"
	if(size==1):
		createInstance()
		flag=False
		break	
	time.sleep(2);





