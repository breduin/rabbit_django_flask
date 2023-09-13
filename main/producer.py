import json
import pika


credentials = pika.PlainCredentials('testuser', 'test')
params = pika.ConnectionParameters(
    'host.docker.internal',
    5672,
    '/',
    credentials,
    connection_attempts=100,
    )
connection = pika.BlockingConnection(params)
channel = connection.channel()


def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(
        exchange='',
        routing_key='admin',
        body=json.dumps(body),
        properties=properties,
        )
