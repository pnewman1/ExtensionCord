CREATE USER 'extension_cord' IDENTIFIED BY 'extension_cord';
CREATE DATABASE extension_cord;
grant all on extension_cord.* to 'extension_cord'@'localhost' identified by 'extension_cord';
flush privileges;
