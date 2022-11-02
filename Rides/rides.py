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
	return "Rides API"


@app.route('/api/v1/rides',methods=["POST"])
def new_ride():
	increment()
	data = request.get_json()
	if("created_by" in data and "timestamp" in data and "source" in data and "destination" in data):
		created_by=data["created_by"]
		tstamp=data["timestamp"]
		intsource=data["source"]
		intdest=data["destination"]
		isvalidDate = True
		try:
			date_object = datetime.strptime(tstamp, "%d-%m-%Y:%S-%M-%H")
			date_object = str(date_object)
		except ValueError:
			isvalidDate = False
		src=int(intsource)
		dst=int(intdest)
		source=0
		dest=0
		with open('AreaNameEnum.csv', 'r') as file:
			reader = csv.reader(file)
			for row in reader:
				if row[0]==intsource:
					source=int(row[0])
				if row[0]==intdest:
					dest=int(row[0])
		url = 'http://assignment3-loadbalancer-1244058846.us-east-1.elb.amazonaws.com/api/v1/users'
		#myobj = {"command": "select","table":"users","where":"username="+"'"+created_by+"'"}
		response = requests.get(url=url, headers={'Origin':'http://ec2-3-225-163-104.compute-1.amazonaws.com'})
		if(response.status_code==204):
			return jsonify ({}),400
		else:
			y = response.json()
			#print(y)
			n = len(y)
			if(source==0 or dest==0 or (source>0 and dest>0 and source==dest) or not(isvalidDate) or (created_by not in y)):
				return jsonify ({}),400
			elif((created_by in y) and isvalidDate):
				url = 'http://3.210.156.166:80/api/v1/db/write'
				myobj = {"command": "insert","table":"rides","column_list":{"created_by":"'"+created_by+"'","time_stamp":"'"+data["timestamp"]+"'","source":"'"+intsource+"'","destination":"'"+intdest+"'"}}
				response = requests.post(url, json = myobj)
				return jsonify ({}),201
	else:
		return jsonify ({}),400


@app.route('/api/v1/rides',methods=["GET"])
def upcoming_rides():
	increment()
	source = request.args.get('source')
	destination = request.args.get('destination')
	current_time = datetime.now()
	src = 0
	dest = 0
	with open('AreaNameEnum.csv', 'r') as file:
		reader = csv.reader(file)
		for row in reader:
			if row[0]==source:
				src=int(row[0])
			if row[0]==destination:
				dest=int(row[0])
	if(src==0 or dest==0 or (src>0 and dest>0 and src==dest)):
		return jsonify({}),400
	else:
		url = 'http://3.210.156.166:80/api/v1/db/read'
		myobj = {"command": "select","table":"rides","where":"source="+str(src)+" and destination="+str(dest)}
		response = requests.post(url, json = myobj)
		x =  response.json()
		l=[]
		for i in x:
			temp = i[2].split(':')[0]
			temp1 = i[2].split(':')[1]
			f = temp.split('-')
			d = int(f[0])
			m = int(f[1])
			yy = int(f[2])
			f1 = temp1.split('-')
			ss = int(f1[0])
			mm = int(f1[1])
			h = int(f1[2])
			if(datetime(yy, m, d, h,mm,ss)>current_time):
				p={"username":i[1],"rideId":str(i[0]),"timestamp":i[2]}
				l.append(p)
		if(len(l)>0):
			return jsonify(l),200
		else:
			return jsonify({}),204


@app.route('/api/v1/rides/<int:rideid>',methods=["GET"])
def ride_details(rideid):
	increment()
	url = 'http://3.210.156.166:80/api/v1/db/read'
	myobj = {"command": "select","table":"rides","where":"rideid="+str(rideid)}
	response = requests.post(url, json = myobj)
	n = len(response.json())
	if(n==1):
		myobj = {"command": "select","table":"ridepool","column_list":["username"],"where":"rideid="+str(rideid)}
		resp1 = requests.post(url, json = myobj)
		ride = response.json()[0]
		q=[]
		for i in resp1.json():
			for j in i:
				q.append(j)
		p={"rideId":str(ride[0]),"created_by":ride[1],"users":q,"timestamp":ride[2],"source":str(ride[3]),"destination":str(ride[4])}
		return jsonify(p),200
	else:
		return '',204


@app.route('/api/v1/rides/<int:rideid>',methods=["POST"])
def join_ride(rideid):
	increment()
	n1=0
	n2=0
	data = request.get_json()
	#print(data)
	if("username" in data):
		username = data["username"]
		url = 'http://assignment3-loadbalancer-1244058846.us-east-1.elb.amazonaws.com/api/v1/users'
		resp1 = requests.get(url=url, headers={'Origin':'http://ec2-3-225-163-104.compute-1.amazonaws.com'})
		if(resp1.status_code==204):
			return jsonify({}),400
		else:
			y = resp1.json()
			url = 'http://3.210.156.166:80/api/v1/db/read'
			obj2 = {"command":"select","table":"rides","where":"rideid="+str(rideid)}
			resp2 = requests.post(url, json = obj2)
			n2 = len(resp2.json())

			if((username in y) and n2==1):
				obj3 = {"command":"select","table":"rides","where":"created_by='"+data["username"]+"' and rideid="+str(rideid)}
				resp3 = requests.post(url, json = obj3)
				n3 = len(resp3.json())

				url1 = 'http://3.210.156.166:80/api/v1/db/write'
				obj = {"command":"select","table":"ridepool","where":"rideid="+str(rideid)+" and "+"username='"+data["username"]+"'"}
				resp = requests.post(url, json=obj)
				if(len(resp.json())==0 and n3==0):
					obj = {"command":"insert","table":"ridepool","column_list":{"rideid":str(rideid),"username":"'"+data["username"]+"'"}}
					resp = requests.post(url1, json=obj)
					return jsonify({}),200
				elif(n3==1):
					return "Creator of ride cannot join the same ride.",400
				else:
					return "Already part of ride.",400
			else:
				return jsonify({}),400
	else:
		return jsonify({}),400


@app.route('/api/v1/rides/<int:rideid>',methods=["DELETE"])
def delete_ride(rideid):
	increment()
	url = 'http://3.210.156.166:80/api/v1/db/read'
	myobj = {"command": "select","table":"rides","where":"rideid="+str(rideid)}
	response = requests.post(url, json = myobj)
	n = len(response.json())
	if(n>0):
		url1 = 'http://3.210.156.166:80/api/v1/db/write'
		obj1 = {"command": "delete","table":"rides","where":"rideid="+str(rideid)}
		resp1 = requests.post(url1, json = obj1)
		obj2 = {"command": "delete","table":"ridepool","where":"rideid="+str(rideid)}
		resp2 = requests.post(url1, json = obj2)
		return jsonify({}),200
	else:
		return jsonify({}),400


@app.route('/api/v1/rides/count',methods=["POST","GET","PUT","PATCH","DELETE","COPY","HEAD","OPTIONS","LINK","UNLINK","PURGE","LOCK","UNLOCK","VIEW"])
def total_rides():
	increment()
	if request.method == 'GET':
		url = 'http://3.210.156.166:80/api/v1/db/read'
		myobj = {"command": "select","table":"rides"}
		response = requests.post(url, json = myobj)
		n = len(response.json())
		l=[]
		l.append(n)
		return jsonify(l),200
	else:
		return jsonify({}),405


@app.route('/api/v1/rides',methods=["PUT","DELETE","PATCH","COPY","HEAD","OPTIONS","LINK","UNLINK","PURGE","LOCK","UNLOCK","VIEW"])
def dummy1():
	increment()
	return jsonify({}),405


@app.route('/api/v1/rides/<int:rideid>',methods=["PUT","PATCH","COPY","HEAD","OPTIONS","LINK","UNLINK","PURGE","LOCK","UNLOCK","VIEW"])
def dummy2(rideid):
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
	app.run(host="0.0.0.0",port=8000)