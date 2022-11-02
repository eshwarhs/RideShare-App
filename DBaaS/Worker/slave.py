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

time.sleep(10)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()
channel1 = connection.channel()
channel.exchange_declare(exchange='sync', exchange_type='fanout')
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='sync', queue=queue_name)
channel1.queue_declare(queue='readQ', durable=True)


url = 'http://orchestrator:80/getsqlcmd'
response = requests.get(url)
if(response.status_code!=204):
	l = response.json()
	for i in l:
		try:
			with sqlite3.connect("rideshare.db") as con:
				print(i)
				cur = con.cursor()
				cur.execute(i)
				con.commit()
		except sqlite3.Error as e:
			print("Database error: %s" % e)
		except Exception as e:
			print("Exception in _query: %s" % e)


def writedb(ch, method, properties, body):
	print("Write DB in slave")
	sql=body.decode("utf-8")
	try:
		with sqlite3.connect("rideshare.db") as con:
			print(sql)
			cur = con.cursor()
			cur.execute(sql)
			con.commit()
	except sqlite3.Error as e:
			print("Database error: %s" % e)
	except Exception as e:
			print("Exception in _query: %s" % e)


def readdb(data):
	sql = data
	print(sql)
	try:
		with sqlite3.connect("rideshare.db") as con:
			print("Inside db")
			cur = con.cursor()
			cur.execute(sql)
			rows = cur.fetchall()
			con.commit()
			print("Exit")
		return rows
	except sqlite3.Error as e:
		print("Database error: %s" % e)
	except Exception as e:
		print("Exception in _query: %s" % e)

def on_request(ch, method, props, body):
	data = body.decode("utf-8")
	response = readdb(data)
	print(json.dumps(response))
	ch.basic_publish(exchange='',
					routing_key=props.reply_to,
					properties=pika.BasicProperties(correlation_id = \
					props.correlation_id),
					body=json.dumps(response))
	print(props.correlation_id)
	ch.basic_ack(delivery_tag=method.delivery_tag)


#channel.basic_qos(prefetch_count=1)
channel1.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue_name, on_message_callback=writedb, auto_ack=True)
#channel.basic_consume(queue='syncQ', on_message_callback=writedb)
channel1.basic_consume(queue='readQ', on_message_callback=on_request)
channel.start_consuming()
channel1.start_consuming()