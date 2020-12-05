#!/usr/bin/env python
import json
#import datetime
import csv
import shutil
import os
import re
from subprocess import Popen, run, PIPE
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

metrics = ["cpu_user", "cpu_kernel", "ram_used", "disk_IO", "network_IN", "network_OUT"]
fields = ['Date', 'Machine', 'Metric', 'Value' , 'Unit']

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/listVMs")
def listVMs():
	output = {}
	output['entry'] = run(['vboxmanage list vms'], shell=True, stdout=PIPE)
	output['entry'] = str(output['entry'])
	output['vms'] = output['entry'].split("stdout=b'")[1]
	output['vms'] = output['vms'].split("\\n")
	return json.dumps(output)

@app.route("/showVMdetail")
def showVMdetail():
	vm = request.args.get('vm_name')
	print (vm)
	output = {}
	output['entry'] = run(['vboxmanage showvminfo ' + vm + ' --machinereadable'], shell=True, stdout=PIPE)
	output['entry'] = str(output['entry'])
	output['entry'] = output['entry'].split("\\n")
	return json.dumps(output)

@app.route("/launchVM")
def launchVM():
	vm = request.args.get('vm_name')
	print (vm)

	output = {}
	stream = run(['vboxmanage startvm ' + vm], shell=True, stdout=PIPE)
	return json.dumps(output)

@app.route("/enableMetrics")
def enableMetrics():
    #run('mv ./data/*.csv ./data_old/')
    files = os.listdir("./data")
    for file in files:
        shutil.move(f"./data/{file}", "./data_old")
    print(files)
    dt = datetime.now()
    dt_string = dt.strftime("%d-%m-%Y-%H-%M-%S")
    #for i in range(len(metrics)):
        #metrics[i] = metrics[i] + dt_string + ".csv"
        #with open("data/" + metrics[i], "w") as csvfile:
            #csvwriter = csv.writer(csvfile)
            #csvwriter.writerow(fields)
    currentCSV = dt_string + ".csv"
    with open("data/" + currentCSV, "w") as csvfile:
        csvwriter = csv.writer(csvfile)
    #print(metrics)
    vm = request.args.get('vm_name')
    #print(vm)
    output = {}
    stream = run(['vboxmanage metrics setup'], shell=True, stdout=PIPE)
    #stream = run(['vboxmanage metrics enable --list'], shell=True, stdout=PIPE)
    return json.dumps(output)

@app.route("/vmScreenshot")
def screenshot():
    print("Screenshot activated")
    output = {}
    output['vms'] = run(['vboxmanage list runningvms'], shell=True, stdout=PIPE)
    output['vms'] = str(output['vms'])
    pattern = r'"([A-Za-z0-9_\./\\-]*)"'
    output['vms'] = re.findall(pattern, output['vms'])
    print(output['vms'])
    cwd = os.getcwd();
    print(cwd)
    dirCheck = os.path.isdir(cwd + "/screenshots")
    if not os.path.exists(cwd + "/screenshots"):
        os.mkdir(cwd + "/screenshots")
    file = os.listdir("./data")
    file = file[0].replace('.csv', '')
    print(file)
    dt = datetime.now()
    dt_string = dt.strftime("%d-%m-%Y-%H-%M-%S")
    for vm in output['vms']:
        stream = run(['vboxmanage controlvm ' + vm + ' screenshotpng ' + cwd + '/screenshots/' + file + '_' + dt_string + '_' + vm + ".png"], shell=True, stdout=PIPE)
    return "iPutThisHereSoIDontGetAnError"

@app.route("/queryMetrics")
def queryMetrics():
    vm = request.args.get('vm_name')
    #print(vm)
    output = {}
    #print(run(['vboxmanage metrics query'], shell=True, stdout=PIPE))
    output['entry'] = run(['vboxmanage metrics query'], shell=True, stdout=PIPE)
    output['entry'] = str(output['entry'])
    output['entry'] = ' '.join(output['entry'].split())
    output['entry'] = output['entry'].split("\\n")
    #print(output['entry'])
    dt = datetime.now()
    dt_string = dt.strftime("%d-%m-%Y-%H:%M:%S")
    output['dt'] = dt_string
    output['metrics'] = {}
    j = 0;

    for i in range(4,len(output['entry'])):
        #print(output['entry'][i])
        sss = output['entry'][i].split()
        #print (sss)
        if len(sss) > 1:
            if sss[0] not in output['metrics']:
                output['metrics'][sss[0]] = []
                #print(sss);
            if len(sss) == 3:
                output['metrics'][sss[0]].append([sss[1], sss[2]])
            if len(sss) == 4:
                output['metrics'][sss[0]].append([sss[1], sss[2], sss[3]])
                #print (sss[0], sss[1], sss[2])
			##else:
				##output['metrics'][sss[0]].append([sss[1], 'NA'])

    file = os.listdir("./data")
    #PARSE INTO CSV
    writeFormat = [dt_string]
    for host in output['metrics']:
        if host != 'host':
            #writeFormat.append(host);
            #CPU
            #writeFormat.append(output['metrics'][host][0][0])
            sHost = host + "_CPU_User"
            writeFormat.append(sHost)
            temp = output['metrics'][host][0][1].replace('%', '')
            writeFormat.append(temp)
            writeFormat.append('%')
            #print(writeFormat)
            #KERNEL
            sHost = host + "_CPU_Kernel"
            #writeFormat.append(output['metrics'][host][4][0])
            writeFormat.append(sHost)
            temp = output['metrics'][host][4][1].replace('%', '')
            writeFormat.append(temp)
            writeFormat.append('%')
            #print(writeFormat)
            #RAM
            sHost = host + "_RAM_Used"
            #writeFormat.append(output['metrics'][host][8][0])
            writeFormat.append(sHost)
            writeFormat.append(output['metrics'][host][8][1])
            writeFormat.append(output['metrics'][host][8][2])
            #print(writeFormat)
            #DISK
            sHost = host + "_DISK_Used"
            #writeFormat.append(output['metrics'][host][12][0])
            writeFormat.append(sHost)
            writeFormat.append(output['metrics'][host][12][1])
            writeFormat.append(output['metrics'][host][12][2])
            #print(writeFormat)
            #NETWORK IN
            sHost = host + "_NET_In"
            #writeFormat.append(output['metrics'][host][16][0])
            writeFormat.append(sHost)
            writeFormat.append(output['metrics'][host][16][1])
            writeFormat.append(output['metrics'][host][16][2])
            #print(writeFormat)
            #NETWORK OUT
            sHost = host + "_NET_Out"
            #writeFormat.append(output['metrics'][host][20][0])
            writeFormat.append(sHost)
            writeFormat.append(output['metrics'][host][20][1])
            writeFormat.append(output['metrics'][host][20][2])
            #print(writeFormat)

    with open("data/" + file[0], "a") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(writeFormat)

    #for host in output['metrics']:
    #    writeFormat = [dt_string, host]
    #    if host != 'host':
    #        #CPU
    #        writeFormat.append(output['metrics'][host][0][0])
    #        temp = output['metrics'][host][0][1].replace('%', '')
    #        writeFormat.append(temp)
    #        writeFormat.append('%')
    #        with open("data/" + metrics[0], "a") as csvfile:
    #            csvwriter = csv.writer(csvfile)
    #            csvwriter.writerow(writeFormat)
    #        print(writeFormat)
    #        #KERNEL
    #        del writeFormat[4]
    #        del writeFormat[3]
    #        del writeFormat[2]
    #        writeFormat.append(output['metrics'][host][4][0])
    #        temp = output['metrics'][host][4][1].replace('%', '')
    #        writeFormat.append(temp)
    #        writeFormat.append('%')
    #        with open("data/" + metrics[1], "a") as csvfile:
    #            csvwriter = csv.writer(csvfile)
    #            csvwriter.writerow(writeFormat)
    #        print(writeFormat)
    #        #RAM
    #        del writeFormat[4]
    #        del writeFormat[3]
    #        del writeFormat[2]
    #        writeFormat.append(output['metrics'][host][8][0])
    #        writeFormat.append(output['metrics'][host][8][1])
    #        writeFormat.append(output['metrics'][host][8][2])
    #        with open("data/" + metrics[2], "a") as csvfile:
    #            csvwriter = csv.writer(csvfile)
    #            csvwriter.writerow(writeFormat)
    #        print(writeFormat)
    #        #DISK
    #        del writeFormat[4]
    #        del writeFormat[3]
    #        del writeFormat[2]
    #        writeFormat.append(output['metrics'][host][12][0])
    #        writeFormat.append(output['metrics'][host][12][1])
    #        writeFormat.append(output['metrics'][host][12][2])
    #        with open("data/" + metrics[3], "a") as csvfile:
    #            csvwriter = csv.writer(csvfile)
    #            csvwriter.writerow(writeFormat)
    #        print(writeFormat)
    #        #NETWORK IN
    #        del writeFormat[4]
    #        del writeFormat[3]
    #        del writeFormat[2]
    #        writeFormat.append(output['metrics'][host][16][0])
    #        writeFormat.append(output['metrics'][host][16][1])
    #        writeFormat.append(output['metrics'][host][16][2])
    #        with open("data/" + metrics[4], "a") as csvfile:
    #            csvwriter = csv.writer(csvfile)
    #            csvwriter.writerow(writeFormat)
    #        print(writeFormat)
    #        #NETWORK OUT
    #        del writeFormat[4]
    #        del writeFormat[3]
    #        del writeFormat[2]
    #        writeFormat.append(output['metrics'][host][20][0])
    #        writeFormat.append(output['metrics'][host][20][1])
    #        writeFormat.append(output['metrics'][host][20][2])
    #        with open("data/" + metrics[5], "a") as csvfile:
    #            csvwriter = csv.writer(csvfile)
    #            csvwriter.writerow(writeFormat)
    #        print(writeFormat)

    return json.dumps(output)

if __name__ == "__main__":
    #socketio.run(app, host='0.0.0.0',port=9123,debug=True)
    app.run(host='0.0.0.0',port=7234,debug=True)
