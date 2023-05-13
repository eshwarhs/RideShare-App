# RideShare API

Basic Requrirements to run the code:
- Docker and Docker-Compose
- Flask, Python

### Steps to run the code:
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
