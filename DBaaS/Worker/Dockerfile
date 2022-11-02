FROM tiangolo/uwsgi-nginx-flask:python3.7
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python db.py
CMD [ "sh", "-c", "sleep 1 && python -u worker.py" ]