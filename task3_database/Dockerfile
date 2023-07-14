FROM mysql:debian
COPY Users.txt /var/lib/mysql-files/
RUN sed -i 's/NULL/\/var\/lib\/mysql-files\//' /etc/mysql/my.cnf
COPY init.sql /docker-entrypoint-initdb.d/
RUN apt-get -y update
RUN apt-get install -y nano