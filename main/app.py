import requests

from dataclasses import dataclass
from flask import Flask, jsonify, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

from producer import publish

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:root@db/main'
CORS(app)


db = SQLAlchemy(app)


@dataclass
class Product(db.Model):
    id: int
    title: str
    image: str
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    title = db.Column(db.String(200))
    image = db.Column(db.String(200))


class ProductUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)

    UniqueConstraint('user_id', 'product_id', name='user_product_unique')


@app.route('/api/products')
def index():
    return jsonify(Product.query.all())


@app.route('/api/products/<int:pid>/like', methods=['POST'])
def like(pid):
    req = requests.get('http://host.docker.internal:8000/api/user')
    jsn = req.json()
    try:
        product_user = ProductUser(user_id=jsn['id'], product_id=pid)
        db.session.add(product_user)
        db.session.commit()

        publish('product_liked', pid)
    except Exception as e:
        print(e)
        abort(400, 'You are already liked this product!')

    return jsonify({'message': 'success'}) 


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
