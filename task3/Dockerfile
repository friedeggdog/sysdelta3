FROM ubuntu
MAINTAINER friedeggwhale
RUN apt-get -y update
RUN apt-get install -y python3
RUN apt-get install -y nano
RUN apt-get install -y python3-pycryptodome
RUN apt-get install -y python3-mysql.connector
COPY echo-serverdocker.py /
RUN mkdir /home/files
CMD ["python3", "-u", "/echo-serverdocker.py"]
