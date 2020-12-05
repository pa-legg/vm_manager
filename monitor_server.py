import socket
import os
import json
import pickle
import datetime
import csv
import shutil
import os
import re
import psutil
from subprocess import Popen, run, PIPE

from _thread import *

out_file = str(datetime.datetime.now())
out_file = out_file.replace('-','').replace(':','').split('.')[0].replace(' ','_')
out_file = "./data/" + out_file + '_server.json'
print(out_file)

empty = []
with open(out_file, 'w') as fd:
    json.dump(empty, fd, sort_keys=True, indent=4)

def write_psutil(data):
    with open(out_file, 'a') as fd:
        json.dump(data, fd, sort_keys=True)

ServerSocket = socket.socket()
host = '0.0.0.0'
port = 1233
ThreadCount = 0
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waitiing for a Connection..')
ServerSocket.listen(5)


def threaded_client(connection):
    connection.send(str.encode('Welcome to the Server\n'))
    while True:
        try:
            data = connection.recv(16000)
            print ("Received: ", len(data))

            data = data.decode('utf-8')
            #data = json.loads(data)

            print (data)
            
            if not data:
                break
            reply = "Received Thanks"
            connection.send(str.encode(reply))

            write_psutil(data)

            #take_screenshot()
            #query_metrics()

            
        except Exception as e:
            print ("Exception: ", e)
            break
    print ("Connection closed")
    connection.close()

while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, ))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
ServerSocket.close()