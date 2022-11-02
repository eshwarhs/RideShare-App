import pika
import json
from flask import Flask,render_template,jsonify,request,abort
import requests
import sqlite3
import re
import csv
from datetime import datetime

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='writeQ', durable=True)
channel1 = connection.channel()
channel1.exchange_declare(exchange='sync', exchange_type='fanout')


def writedb(ch, method, properties, body):
	sql=body.decode("utf-8")
	ch.basic_ack(delivery_tag=method.delivery_tag)
	try:
		with sqlite3.connect("rideshare.db") as con:
			print(sql)
			cur = con.cursor()
			cur.execute(sql)
			con.commit()
			channel1.basic_publish(
				exchange='sync',
				routing_key='',
				body=sql,
				properties=pika.BasicProperties(
					delivery_mode=2,  # make message persistent
				))
	except sqlite3.Error as e:
			print("Database error: %s" % e)
	except Exception as e:
			print("Exception in _query: %s" % e)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='writeQ', on_message_callback=writedb)
channel.start_consuming()