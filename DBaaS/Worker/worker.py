import pika
import json
from flask import Flask,render_template,jsonify,request,abort
import requests
import sqlite3
import re
import subprocess
import csv
import time
import socket
from datetime import datetime
from kazoo.client import KazooClient
import subprocess

zk = KazooClient(hosts='zoo:2181')
zk.start()

cmd = "cat /proc/self/cgroup | head -1"
xx = subprocess.check_output(cmd, shell=True)
xx = xx.decode("utf-8")
xx = xx.split('/')
y = xx[-1].strip('\n')
print(y)

url = 'http://172.17.0.1:5555/containers/'+y+'/top'
resp = requests.get(url)
res = resp.json()
print(res)
yy = y+";"+str(res["Processes"][0][2])+";"+"slave"
path = zk.create("/workers/node", value = yy.encode("utf-8"), ephemeral=True, sequence=True)
print(path)

print("Worker Container")

abc = subprocess.Popen(["python","-u","slave.py"])

print("Later")

@zk.DataWatch(path)
def change_to_master(data,stat):
	d = data.decode('utf-8')
	role = d.split(';')[2]
	if(role=="master"):
		print("I am the master")
		abc.kill()
		subprocess.Popen(["python","-u","master.py"])
		#channel.basic_cancel(consumer_tag="")
		#channel1.basic_cancel(consumer_tag="")
		#channel.stop_consuming(consumer_tag=None)
		#channel1.stop_consuming(consumer_tag=None)
		#channelx = connection.channel()
		#channelx.queue_declare(queue='hello')
		#channelx.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)
		#channel.start_consuming()

while True:
	pass