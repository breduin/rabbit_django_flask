import json
import pika

from app import (
    app,
    db,
    Product,
    )


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


channel.queue_declare(queue='main')


def callback(ch, method, properties, body):
    print('Received in main')
    data = json.loads(body)
    print(data)

    if properties.content_type == 'product_created':
        product = Product(
            id=data['id'],
            title=data['title'],
            image=data['image'],
            )
        with app.app_context():
            db.session.add(product)
            db.session.commit()
        print('Product created')

    elif properties.content_type == 'product_updated':
        with app.app_context():
            product = Product.query.get(data['id'])
            product.title=data['title']
            product.image=data['image']            
            db.session.commit()
        print('Product updated')

    elif properties.content_type == 'product_deleted':
        with app.app_context():
            product = Product.query.get(data['id'])
            db.session.delete(product)
            db.session.commit()
        print('Product deleted')


channel.basic_consume(queue='main', on_message_callback=callback, auto_ack=True)


print('Starting consuming')

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
    print('Stopped consuming')


channel.close()
