import pika
import sys
import os
import json
import datetime
import requests
from pymongo import MongoClient


db_connection = MongoClient("mongodb://mongodb:Cc03Wz5XX3iI3uY3@mongo")
db_base = db_connection["phone"]
coll_phone = db_base["phone"]
coll_userkey = db_base['userkey']

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        'rabbitmq', 5672, 'mkt', pika.PlainCredentials('rabbit', 'mrl2X0jwnYuCCiKFTshG7WKyOAhfDo')))
    channel = connection.channel()

    channel.queue_declare(queue='incoming')
    tmpIncoming = {}
    # tmpExternal = {}

    def callback(ch, method, properties, body: bytearray):
        try:
            # Парсим строку
            srcJson = json.loads(str(body.decode('utf-8')).replace("\'", "\""))
            srcJson["time"] = datetime.datetime.fromtimestamp(
                srcJson["time"]).strftime('%Y-%m-%d %H:%M:%S')

            # Определяем направление соединения
            if srcJson['direction'] == 'incoming':
                # Определяем начальный статус
                if srcJson['state'] == 'START':
                    # Создаем переменную. Ответ = false, можно закрывать = false, Приоритетная линия
                    if srcJson['to'] == '83912051045':
                        tmpIncoming[srcJson['uuid']] = [False, False, True]
                    else:
                        tmpIncoming[srcJson['uuid']] = [False, False, False]
                    # Обновление статуса при входящем звонке
                    coll_phone.delete_one({'$and': [{'client': srcJson['from']}, {'status': 1}]})
                if srcJson['state'] == 'ANSWER' and srcJson['uuid'] in tmpIncoming:
                    tmpIncoming[srcJson['uuid']][0] = True
                if srcJson['state'] == 'END' and srcJson['uuid'] in tmpIncoming:
                    tmpIncoming[srcJson['uuid']][1] = True
                if srcJson['state'] == 'HANGUP' and srcJson['uuid'] in tmpIncoming and tmpIncoming[srcJson['uuid']][1] == True:
                    try:
                        srcJson['callstatus']
                        insDict = {"client": srcJson['from'], "time": srcJson['time'], "status": 0,
                                   "recordUrl": srcJson["recordUrl"], "duration": srcJson["duration"], "important": tmpIncoming[srcJson['uuid']][2]}
                    except Exception as e:
                        # print(srcJson)
                        print(e)
                        insDict = {
                            "client": srcJson['from'], "time": srcJson['time'], "status": 1, "important": tmpIncoming[srcJson['uuid']][2]}
                        #sendMessage(srcJson['time'], srcJson['from'])
                    finally:
                        print(insDict)
                        coll_phone.insert_one(insDict)
                        tmpIncoming.pop(srcJson['uuid'])
                        try:
                            insUserKey = {'userkey': srcJson['userkey']}
                            print(insUserKey)
                            print(srcJson['to'])
                            coll_userkey.update_one(
                                filter={
                                    'operator': srcJson['to'],
                                },
                                update={
                                    '$set': insUserKey,
                                },
                                upsert=True
                            )
                        except Exception as e:
                            print(e)

            if srcJson['direction'] == 'external':
                # coll_phone.update_one({'$and': [{'client': srcJson['to']}, {'status': 1}]}, {
                #                       '$set': {'status': 2}})
                r = coll_phone.update_one({'$and': [{'client': {'$regex': srcJson['to']}}, {'status': 1}]}, {
                                      '$set': {'status': 2, 'callid': srcJson['uuid']}})
                if srcJson['state'] == 'HANGUP':
                    try:
                        coll_phone.update_one({'callid':srcJson['uuid']}, {'$set': {'recordUrl': srcJson['recordUrl']}})
                    except Exception as e:
                        print(e)
                print(r)

        except Exception as e:
            print(e.with_traceback)
            print(e)
            # print(None)
            exit()

    channel.basic_consume(
        queue='incoming', on_message_callback=callback, auto_ack=True)

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
