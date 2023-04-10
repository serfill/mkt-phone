import pika
from flask import Flask, jsonify, request
import json
import time
import threading

app = Flask(__name__)
exch = 'mobilon'
server = 'rabbitmq'
r_user = 'rabbit'
r_pass = 'mrl2X0jwnYuCCiKFTshG7WKyOAhfDo'


class RMQ(object):
    def __init__(self) -> None:
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            'rabbitmq', 5672, 'mkt', pika.PlainCredentials('rabbit', 'mrl2X0jwnYuCCiKFTshG7WKyOAhfDo')))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange='mobilion', exchange_type='fanout')
        result = self.channel.queue_declare(queue='incoming')
        self.channel.queue_bind(exchange='mobilion', queue=result.method.queue)

    def call(self, n):
        self.response = None
        self.channel.basic_publish(
            exchange='mobilion', routing_key='', body=str(n))
        self.channel.close()
        self.connection.close()


@app.route("/")
def default():
    return ("Ok")


@app.route("/api/call/add/", methods=["POST"])
def rm():
    try:
        d: dict = request.get_json(True)
        s: str = json.dumps(d).encode('utf8', errors="ignore")
        rp = RMQ()
        threading.Thread(target=rp.call(str(d),)).start()
    except Exception as e:
        app.logger.error(e)
    finally:
        return ("Ok")


if __name__ == "__main__":
    app.debug = False
    app.run(host="0.0.0.0", port=5000)
    app.run(port=5000)
