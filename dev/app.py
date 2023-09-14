import pika
import sys
import os
import json
import datetime
import re


class msg:
    def __init__(self, message):
        self.body: bytearray = message
        self.decode: str = self.body.decode('utf-8')
        self.json: json = json.loads(self.decode.replace("\'", "\""))
        self.dict: dict = dict(self.json)

        if self.dict["direction"] == "incoming":
            if self.dict["state"] == "START":
                # Добавляем в базу информацию о начале вызова
                self.incStart()
            if self.dict["state"] == "HANGUP":
                # добавляем информацию об окончании вызова
                print("Конец")

        # if self.dict["direction"] == "external":
        #     self.incoming()

        #     self.external()

    def incStart(self):
        res = {
            "client": self.dict['from'],
            "to": self.dict['to'],
            "time": datetime.datetime.fromtimestamp(
                self.dict["time"]).strftime('%Y-%m-%d %H:%M:%S'),
            "important": self.checkImportant(),
            "uuid": self.dict['uuid'],
            "status": -1,
            "checkNumer": self.checkNumber(),

        }

        print(res)
        # client: str =
        # time: str = datetime.datetime.fromtimestamp(
        #     self.dict["time"]).strftime('%Y-%m-%d %H:%M:%S')
        # status: int = int(not "callstatus" in self.dict.keys())
        # important: bool = self.checkImportant()
        # uuid: str = self.dict['uuid']

        # res = {"client": client,
        #        "time": time,
        #        "status": status,
        #        "important": important,
        #        "uuid": uuid}

        # if status == 0:
        #     res["recordUrl"] = self.dict["recordUrl"]

    def external(self):
        print("sdf")

    def checkImportant(self) -> bool:
        ImportantList = ['83912051045', '83912051046']
        return True if self.dict["to"] in ImportantList else False

    def checkNumber(self) -> bool:
        return True if re.match(r'8\d{10}', self.dict['from']) and len(self.dict['from']) == 11 else False


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        "192.168.0.20", 5672, "mkt", pika.PlainCredentials(
            "rabbit", "mrl2X0jwnYuCCiKFTshG7WKyOAhfDo")
    ))
    channel = connection.channel()

    def callback(ch, method, properties, body: bytearray):
        m = msg(body)

    channel.basic_consume(
        queue='test', on_message_callback=callback, auto_ack=False)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
