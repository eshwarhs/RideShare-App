# Cloud Computing Project - RideShare API

Basic Requrirements to run the code:
- Docker and Docker-Compose
- Flask, Python


### Assignment 1
Steps to run the code:
```sh
$ pip install -r requirements.txt
$ python app.py
```

### Assignment 2
Steps to run the code:
- Change the IP addresses in the code accordingly. Setup the AWS instance.
```sh
$ sudo docker-compose up --build --force-recreate
```

### Assignment 3
Steps to run the code:
- Change the IP addresses in the code accordingly. Setup the AWS instances.
- Create the Load Balancer and configure everything.
- On the Users' instance: 
    ```sh
    $ sudo docker-compose up --build --force-recreate
    ```
- On the Rides' instance: 
    ```sh
    $ sudo docker-compose up --build --force-recreate
    ```
    
### Project
Steps to run the code:
- Create a new instance along with previous Rides and Users instance. Name the instance as DBaaS
- Change the IP addresses and code in Users and Rides instances accordingly.
- Enable the Docker Engine API on DBaaS instance:
    ```sh
        $ sudo nano /lib/systemd/system/docker.service
        $ ExecStart=/usr/bin/dockerd -H fd:// -H=tcp://0.0.0.0:5555
        $ sudo systemctl daemon-reload
        $ sudo service docker restart
    ```
- Download the DBaaS folder to the Instance
```sh
$ cd DBaas/Worker
$ sudo docker build -t worker .
$ cd ..
$ sudo docker-compose up --build --force-recreate
```
