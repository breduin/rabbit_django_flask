import json
import pika

from admin.wsgi import *

from products.models import Product


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


channel.queue_declare(queue='admin')


def callback(ch, method, properties, body):
    print('Received in admin')
    pid = json.loads(body)
    product = Product.objects.get(id=pid)
    product.likes += 1
    product.save()
    print('Product likes increased!')


channel.basic_consume(queue='admin', on_message_callback=callback, auto_ack=True)


print('Starting consuming')

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
    print('Stopped consuming')


channel.close()
