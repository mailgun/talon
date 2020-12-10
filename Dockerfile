FROM ubuntu:latest

RUN apt-get -yqq update
RUN apt-get install -yqq python3
RUN apt-get -yqq install python3-pip

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt
RUN pip3 install .

ENTRYPOINT [ "python3" ]

CMD [ "/app/talon/web/bootstrap.py" ]
