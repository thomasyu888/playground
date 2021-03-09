#!/usr/bin/env python
import synapseclient

import pika
import uuid

class SubmissionRpcClient(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return self.response


submission_rpc = SubmissionRpcClient()

print(" [x] Requesting fib(30)")
syn = synapseclient.login()
submissions = syn.tableQuery("select id from syn22141919 where status = 'INVALID'")
submissionsdf = submissions.asDataFrame()
for submission in submissionsdf.id:
    print(submission)
    response = submission_rpc.call(submission)

    print(" [.] Got %r" % response)
