CREATE DATABASE users;
USE users;
create table uandp(Username CHAR(20) UNIQUE, Pass CHAR(9));
LOAD DATA INFILE '/var/lib/mysql-files/Users.txt' INTO TABLE uandp FIELDS TERMINATED BY ' ' LINES TERMINATED BY '\n';
