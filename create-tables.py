from config_db import db_connection_cfg

from DBcm3 import UseDatabase, DbConnectError, DbCredentialsError, SQLError

with UseDatabase(db_connection_cfg) as cursor:
   _SQL=\
     """
       create table logins (
          id int auto_increment primary key,
          login varchar(32) not null,
          password varchar(32) not null,
          ts timestamp default current_timestamp,
          browser_str varchar(256) not null
       )
     """

   cursor.execute(_SQL)
   
   _SQL=\
     """
     create table blogs (
        id int auto_increment primary key,
        title varchar(32) not null,
        content text not null,
        ts timestamp default current_timestamp);

     """

   cursor.execute(_SQL)

