#!/usr/bin/env python
import pika
import synapseclient

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

syn = synapseclient.login()
submissions = syn.tableQuery("select id from syn22141919 where status = 'INVALID'")
submissionsdf = submissions.asDataFrame()
for submission in submissionsdf.id:
    print(submission)
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=submission,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
    ))
    print(f" [x] Sent {submission}")
connection.close()