from urllib import request
from flask import Flask, jsonify, render_template, url_for, request
import json
import datetime
from pymongo import MongoClient

CONNECTION_STRING = "mongodb://mongodb:Cc03Wz5XX3iI3uY3@mongo"

db_connection = MongoClient(CONNECTION_STRING)
db_base = db_connection["phone"]
coll_call = db_base["phone"]
coll_history = db_base["history"]

app = Flask(__name__)

internal = {}
external = {}
State = ""


@app.route("/")
def root():
    return "Ok"


# @app.route("/api/call/add/", methods=["POST"])
# def ApiCallAdd():
#     r_data = request.get_json()
#     r_data["time"] = datetime.datetime.fromtimestamp(
#         r_data["time"]).strftime('%Y-%m-%d %H:%M:%S')

#     # Если вызов входящий
#     if r_data["direction"] == "incoming":
#         # Если стартует новая сессия, добавляем запись в словарь.
#         if r_data["state"] == "START":
#             internal[r_data["uuid"]] = [False, False]
#         # Если получен ответ, проверяем есть ли запись в словаре, если есть, обновляем статус соединения
#         if r_data["state"] == "ANSWER" and r_data["uuid"] in internal:
#             internal[r_data["uuid"]][0] = True
#         # Если разговор статус END, отмечаем флаг зарвершения разговора
#         if r_data["state"] == "END" and r_data["uuid"] in internal:
#             internal[r_data["uuid"]][1] = True
#         # Если разговор статус HANGUP и
#         if r_data["state"] == "HANGUP" and r_data["uuid"] in internal and internal[r_data["uuid"]][1] == True:
#             print(r_data)
#             if internal[r_data["uuid"]][0] == True:
#                 State = 0
#             else:
#                 State = 1
#             internal.pop(r_data["uuid"])
#             # Добавляем запись в базу данных
#             res = {"Operator": r_data["to"], "Client": r_data["from"],
#                    "CallTime": r_data["time"], "State": State}
#             if State == 0:
#                 res["Record"] = r_data["recordUrl"]
#             coll_call.insert_one(res)
#             coll_history.insert_one(res)

#     # Если вызов исходящий
#     if r_data["direction"] == "external":
#         # Добавляем запись о совершении исходящего звонка
#         if r_data["state"] == "PREANSWER":
#             external[r_data["to"]] = [False]
#             coll_call.update_many(
#                 {'State': {'$in': [1, 3]}, 'Client': r_data["to"]}, {'$set': {"State": 4}})
#         # Дальнейшие действия зависят от того добавили ли мы в справочник исходящий номер
#         if r_data["to"] in external:
#             # Если на том конце ответили, меняем статус
#             if r_data["state"] == "ANSWER":
#                 external[r_data["to"]][0] = True
#             # Если положили трубку делаем финальную обработку
#             if r_data["state"] == "HANGUP":
#                 # Присваиваем в поле RecallTime значение поля time и значения поля State по умолчанию =3 (Абонент не взял трубку)
#                 res = {"RecallTime": r_data["time"]}
#                 res["State"] = 3
#                 # Если ответ был делаем дополнительные поля
#                 if external[r_data["to"]][0] == True:
#                     res["Record"] = r_data["recordUrl"]
#                     res["State"] = 2
#                 # Добавляем запись в таблицу. Меняем все поля где абонент = исходящий номер и номер
# #                coll_call.update_one(
# #                    {'State': {'$in': [4]}, 'Client': r_data["to"]}, {'$set': res})
#                 coll_call.update_one(
#                     {'State': 4, 'Client': r_data["to"]}, {'$set': res})
#                 external.pop(r_data["to"])
#     return ({"StatusCode": 200})


@app.route("/web/call/")
def WebCall():
    call = coll_call.find().sort('time',-1)
    return render_template("WebCall.html", call=call)

@app.route("/web/call/test/")
def GetTest():
    call = coll_call.find().sort('time',-1)
    return render_template("TestCall.html", call=call)

@app.route("/web/call/status/<id>")
def WebCallStatus(id):
    call = coll_call.find({"status": int(id)}).sort('time',-1)
    return render_template("WebCall.html", call=call)


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5001)
