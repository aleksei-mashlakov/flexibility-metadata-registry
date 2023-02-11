FROM locustio/locust:latest

COPY ./docker_containers/loadtesting/app /app
ADD ./logs /app/logs
ADD ./platform /app/platform
ADD ./config /app/config
ADD ./docker_containers/loadtesting/app/locustfile.py /app/platform/locustfile.py

RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

WORKDIR /app

ENTRYPOINT locust -f /app/platform/locustfile.py --host https://localhost:443 \
                                                 --users 1000 \
                                                 --spawn-rate 1
