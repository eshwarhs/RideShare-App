from flask import Flask,render_template,jsonify,request,abort
import requests
import sqlite3
import re
import csv
from datetime import datetime


app=Flask(__name__)

def increment():
	f=open("count.txt", "r")
	count = f.read()
	f.close()
	count = int(count)
	count=count+1
	f=open("count.txt", "w")
	f.write(str(count))
	f.close()


@app.route('/')
def hello_world():
	return "Users API"


@app.route('/api/v1/users',methods=["PUT"])
def add_user():
	increment()
	data = request.get_json()
	if("username" in data and "password" in data):
		new_username = request.get_json()["username"]
		new_passw = (request.get_json()["password"]).lower()
		url = 'http://3.210.156.166:80/api/v1/db/read'
		myobj = {"command": "select","table":"users","where":"username="+"'"+new_username+"'"}
		response = requests.post(url, json = myobj)
		y = response.json()
		n = len(y)
		if(n==0 and re.match(r"[0-9a-f]{40}", new_passw) and len(new_username)>0 and len(new_passw)==40):
			url = 'http://3.210.156.166:80/api/v1/db/write'
			myobj = {"command": "insert","table":"users","column_list":{"username":"'"+new_username+"'","password":"'"+new_passw+"'"}}
			response = requests.post(url, json = myobj)
			return jsonify ({}),201
		else:
			return jsonify ({}),400
	else:
		return jsonify ({}),400


@app.route('/api/v1/users/<username>',methods=["POST","GET","PUT","PATCH","DELETE","COPY","HEAD","OPTIONS","LINK","UNLINK","PURGE","LOCK","UNLOCK","VIEW"])
def remove_user(username):
	increment()
	if request.method == 'DELETE':
		if(username):
			url = 'http://3.210.156.166:80/api/v1/db/read'
			myobj = {"command": "select","table":"users","where":"username="+"'"+username+"'"}
			response = requests.post(url, json = myobj)
			y = response.json()
			n = len(y)
			url = 'http://3.210.156.166:80/api/v1/db/read'
			myobj = {"command": "select","table":"rides","where":"created_by="+"'"+username+"'"}
			response = requests.post(url, json = myobj)
			n1 = len(response.json())
			if(n==1 and n1==0):
				url = 'http://3.210.156.166:80/api/v1/db/write'
				myobj = {"command": "delete","table":"users","where":"username="+"'"+username+"'"}
				response = requests.post(url, json = myobj)
				url = 'http://3.210.156.166:80/api/v1/db/write'
				myobj = {"command": "delete","table":"ridepool","where":"username="+"'"+username+"'"}
				response = requests.post(url, json = myobj)
				return jsonify ({}),200
			elif(n1>0):
				return "This user cannot be deleted as he is associated with a ride.",400
			else:
				return jsonify({}),400
		else:
			return jsonify ({}),400
	else:
		return jsonify({}),405


@app.route('/api/v1/users',methods=["GET"])
def list_users():
	increment()
	url = 'http://3.210.156.166:80/api/v1/db/read'
	myobj = {"command":"select","table":"users","column_list":["username"]}
	response = requests.post(url, json = myobj)
	y = response.json()
	users = [i[0] for i in y]
	#print(users)
	if(len(users)>0):
		return jsonify(users),200
	else:
		return jsonify({}),204

@app.route('/api/v1/users',methods=["POST","PATCH","COPY","HEAD","OPTIONS","LINK","UNLINK","PURGE","LOCK","UNLOCK","VIEW"])
def dummy():
	increment()
	return jsonify({}),405

@app.route('/api/v1/_count',methods=["GET"])
def return_count():
	f=open("count.txt", "r")
	count = f.read()
	f.close()
	count=int(count)
	l=[]
	l.append(count)
	return jsonify(l),200


@app.route('/api/v1/_count',methods=["DELETE"])
def clear_count():
	f=open("count.txt", "w")
	count = 0
	f.write(str(count))
	f.close()
	return jsonify({}),200


@app.route('/api/v1/db/clear',methods=["POST"])
def clear_db():
	url = 'http://3.210.156.166:80/api/v1/db/write'
	myobj = {"command": "delete","table":"users"}
	response = requests.post(url, json = myobj)
	myobj = {"command": "delete","table":"rides"}
	response = requests.post(url, json = myobj)
	myobj = {"command": "delete","table":"ridepool"}
	response = requests.post(url, json = myobj)
	url = 'http://3.210.156.166:80/api/v1/db/clear'
	response = requests.post(url)
	return jsonify({}), 200


if __name__ == '__main__':	
	app.debug=True
	app.run(host="0.0.0.0",port=8080)