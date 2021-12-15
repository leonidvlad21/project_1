
Install
---------

Create virtual environment and install python libraries
------------------------------------------------------------------------
```
python3.9 -m venv venv
on Linux:
source venv/bin/activate
on Windows:
venv/scripts/activate

pip install -r requirements.txt
```

Create mysql database
--------------------------------
```
sudo apt install mysql-server mysql-client
echo 'CREATE DATABASE <database_name>;' | mysql -u <mysql_user_name> -p<mysql_user_password>
cp config_db_template.py config_db.py
```

 edit config.py, set mysql database name, user and password


Create tables in database:
------------------------------------
```
python create-tables.py 
```
Run application:
----------------------
```
python index.py
```


