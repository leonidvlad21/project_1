# works in Client folder with subfolders
# database: 'mysql'

from flask import Flask, render_template, redirect, request, url_for, session,\
     flash
from flask_autoindex import AutoIndex
from werkzeug.exceptions import abort

""" add template_folder """
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'secret 5 key'

# DB configur:
from config_db import db_connection_cfg
app.config ['dbconfig'] = db_connection_cfg

from DBcm3 import UseDatabase, DbConnectError, DbCredentialsError, SQLError

ppath = ".."                           # parent directory
files_index = AutoIndex(app, browse_root=ppath, add_url_rules=False)

### mysql ###

def get_logins() -> list:
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL= """select
            login from logins"""
            cursor.execute(_SQL)
            contents = cursor.fetchall()
            db_logins = [item[0] for item in contents]      # convert to list of str
            return db_logins
    except DbConnectError as err:
	    print('DB connection error: ', str(err))
    except DbCredentialsError as err:
	    print ('User-id/Password issues. Error: ', str(err))
    except SQLError as err:
	    print('Is query correct? Error: ', str(err))

    except Exception as err:
	    print ('DB exception: ', str(err))	
    return []

def logins_request(req: 'flask_request', browser_str) -> None:
	print('Logins_request across ', browser_str)
	with UseDatabase(app.config['dbconfig']) as cursor:
		_SQL= """insert into logins
		(login, password, browser_str)
		values
		(%s, %s, %s)"""
		cursor.execute(_SQL,
		(req.form['login'],
		req.form['password'],
		browser_str))

def get_psw(login_val) -> str:
    with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL= """select
            password from logins
            where login = %s"""
            cursor.execute(_SQL,
            [login_val])
            contents = cursor.fetchall()
            if contents:
                print ('Selected: ', contents[-1])          # get last value
                return contents[-1][0]
            return ''
            
def init():                                                 # void
    print ('Init')
    return True

logins = get_logins()                                       # global
print('logins: ', logins)

  
from checker import check_logged_in
def check_user(user: str):
    return True


@app.route('/logout')
def do_logout() -> str:
    if 'logged_in' in session.keys():
        session.pop('logged_in')
    return 'Now you are logged out'

@app.route('/register', methods=('GET', 'POST'))
def do_register() -> str:
    print('register')
    
    login = request.form.get('login')
    print ('Entered login: ', login)
    msg = 'Input login'
    if request.method == 'POST':
        print ('Post (register)')
        login = request.form['login']
        password = request.form['password']
        if login in logins:
            print ('Login used: ', login)
            msg = 'Login ' + login +\
                  ' already used, enter another'
            return render_template('/register.html', var_msg = msg)
        else:
            print ('Posted login: ', login, ' password: ', password)
            try:
                logins_request(request, request.user_agent.browser)
                logins.append(login)
                do_login(login)
                print ('Registered ', session['name'])
            except Exception as err:
                print('Registering failed. Error: ' + str(err))
   
            return redirect('indexblog')
    
    login = request.form.get('login')
    print ('Entered login: ', login)
    
    return render_template('/register.html', var_msg = msg)

def do_login(login):
    session['name'] = login
    session['logged_in'] = True

@app.route('/exam_3_login', methods=('GET', 'POST'))
def do_login_3():
    print('Login_3')
    session['name'] = 'Unknown'
    if request.method == 'POST':
        print ('Post (login)')
        login = request.form['login']
        password = request.form['password']
        print ('password', password)
        db_password = get_psw(login)
        if password == db_password:
            print ('Password accepted: ', password)
            do_login(login)
            return redirect('indexblog')
    return render_template('exam_3_login.html')

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            with UseDatabase(app.config['dbconfig']) as cursor:
                _SQL= """insert into
                blogs (title, content)
                values (%s, %s)"""
                cursor.execute(_SQL,
                [title, content])

            return redirect(url_for('indexblog'))
    return render_template('create.html')

def get_blogs() -> list:
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL= """select
            * from blogs"""
            cursor.execute(_SQL)
            columns = cursor.description
            res = []
            for value in cursor.fetchall():                 # transform to map list
                tmp = {}
                for (index,column) in enumerate(value):
                    tmp[columns[index][0]] = column
                res.append(tmp)
            return res
    except DbConnectError as err:
	    print('DB connection error: ', str(err))
    except DbCredentialsError as err:
	    print ('User-id/Password issues. Error: ', str(err))
    except SQLError as err:
	    print('Is query correct? Error: ', str(err))

    except Exception as err:
	    print ('DB exception: ', str(err))	
    return 'Error'

def get_blog(post_id) -> dict:
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL= """select
            * from blogs
            where id = %s"""
            cursor.execute(_SQL, [post_id])
            post = cursor.fetchone()
            if post is None:
                abort(404)
            print('get_blog: ', post)
            columns = cursor.description
            res = {}
            for (index,val) in enumerate(post):
                res[columns[index][0]] = val
            print('get_blog result = ', res)
            return res
    except DbConnectError as err:
	    print('DB connection error: ', str(err))
    except DbCredentialsError as err:
	    print ('User-id/Password issues. Error: ', str(err))
    except SQLError as err:
	    print('Is query correct? Error: ', str(err))

    except Exception as err:
	    print ('DB exception: ', str(err))	
    return 'Error'

### 1st page ###

@app.route('/indexblog')                        
def indexblog() -> 'html':
    print('indexblog')
    posts = get_blogs()
    return render_template('indexblog.html', posts = posts,
                           userlogin = ', ' + session['name'] if 'name' in session else '')

@app.route('/<int:post_id>')
def post(post_id):
    print('Post_id', post_id)
    post = get_blog(post_id)
    return render_template('post.html', the_post=post)

@app.route('/download')
def do_download():
    if not 'logged_in' in session.keys() or not session['logged_in']:
                               # Access to files was blocked
        print ('No access')
        return redirect('indexblog')
    print ('Access to files')
    ClientName = 'Clients'
    return redirect(ClientName)

@app.route('/')
@app.route('/<path:path>')
def autoindex(path='.'):
    print ('path: ', path)
    if path == '.':
        print('ClientFiles')
        session['logged_in'] = False
        init()
        return redirect('indexblog')
    return files_index.render_autoindex(path, template='autoindex.html')

if __name__ == '__main__':
    app.run()
