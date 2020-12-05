import socket
import psutil
import datetime
import time
import json
import pickle

def get_single_data():
    show_output = False
    entry = {}
    entry['dt'] = str(datetime.datetime.now())
    entry['machine'] = 'machine1'
    entry['boot_dt'] = str(datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"))
    entry['cpu'] = psutil.cpu_times()
    entry['cpu_percent'] = psutil.cpu_percent()
    entry['network'] = psutil.net_io_counters(pernic=True)
    entry['network_conns'] = psutil.net_connections()
    entry['disk_io_counters'] = psutil.disk_io_counters(perdisk=True)
    entry['memory'] = psutil.virtual_memory()
    entry['swap'] = psutil.swap_memory()
    entry['processes_info'] = []
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name'])
            entry['processes_info'].append(pinfo)
        except psutil.NoSuchProcess:
            pass
    if show_output:
        print(entry)
        print ("\n")
    entry = json.dumps(entry)
    return entry



ClientSocket = socket.socket()
host = '10.10.5.0'
port = 1233

print('Waiting for connection')
try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

Response = ClientSocket.recv(1024)
while True:
    data = get_single_data()
    print ("Sending: ", len(data))
    ClientSocket.send(str.encode(data))
    Response = ClientSocket.recv(1024)
    print(Response.decode('utf-8'))
    time.sleep(5)

ClientSocket.close()
