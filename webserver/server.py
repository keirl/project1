#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following uses the postgresql test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/postgres
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# Swap out the URI below with the URI for the database created in part 2
DATABASEURI = "postgresql://kcl2143:2nz62@104.196.175.120/postgres"

# DATABASEURI = "sqlite:///test.db"

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#

# END SQLITE SETUP CODE
#



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args
  return render_template("index.html")

  
#
#@app.route('/another')
#def another():
#  return render_template("anotherfile.html")


# Example of adding new data to the database
#@app.route('/add', methods=['POST'])
#def add():
#  name = request.form['name']
#  print name
#  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
#  g.conn.execute(text(cmd), name1 = name, name2 = name);
#  return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    #print request.form['username']
    username = request.form['username']
    password = request.form['password']
    print username, password
    cmd = 'SELECT userid FROM users WHERE username=:var1 AND password=:var2 LIMIT 1'
    print cmd
    cursor = g.conn.execute(text(cmd), var1 = username, var2 = password);
    record = cursor.fetchone()
    cursor.close()
    if record is None:
        return redirect('/users/0')
    else:  
        userid = record['userid']
    return redirect('/users/'+str(userid))
    
@app.route('/users/<userid>')
def user(userid):
    userid = int(userid)
    print type(userid)
    if userid == 0:
        return render_template("user_new.html")
    else:
        context = dict(userid = userid)
        context['username'] = 'dude'
        return render_template('user.html',**context)
    
@app.route('/users/add', methods=['POST'])
def user_add():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    bio = request.form['bio']
    cmd = 'INSERT INTO users (email, username, password, bio) VALUES (:var1, :var2, :var3, :var4)'
    
    ## Add integrity checking
    g.conn.execute(text(cmd), var1 = email, var2 = username, var3 = password, var4 = bio);
    cmd = 'SELECT userid FROM users WHERE username=:var1 LIMIT 1'
    cursor = g.conn.execute(text(cmd), var1 = username);
    record = cursor.fetchone()
    userid = record['userid']
    return redirect('/users/'+str(userid))    
        
     
@app.route('/users/<userid>/cookbooks/<action>')
@app.route('/users/<userid>/cookbooks/<action>/<cbid>') 
def cookbooks(userid,action,cbid=None):
     # This is to see the list of cookbooks
    CBID_INCR = '10'
    if cbid is None:
        init_cbid = 0
    elif int(cbid) >= 0:
        init_cbid = int(cbid)
    else:
        init_cbid = 0
    
    context = {}
            
            
    if action == 'view_all': 
        cmd = 'SELECT cbid FROM cookbookowners WHERE userid=:userid ORDER BY cbid LIMIT :cbid_incr OFFSET :offset_value'
        cursor = g.conn.execute(text(cmd),offset_value=str(init_cbid),cbid_incr=CBID_INCR,userid=userid)
        cbid_owned = []
        for record in cursor:
            cbid_owned.append(record['cbid'])
           
        cmd = 'SELECT cbid, description FROM cookbooks ORDER BY cbid LIMIT :cbid_incr OFFSET :offset_value'
        cursor = g.conn.execute(text(cmd),offset_value=str(init_cbid),cbid_incr=CBID_INCR);
        cookbooks = []
        for record in cursor:
            if record['cbid'] in cbid_owned:
                cookbooks.append((record['cbid'],record['description'],'1'))
            else:
                cookbooks.append((record['cbid'],record['description'],'0'))
        
        context['cookbooks'] = cookbooks
        context['userid']=str(userid)
        context['curr_cbid'] = str(init_cbid)
        context['next_cbid'] = str(init_cbid + int(CBID_INCR))
        context['prev_cbid'] = str(max(init_cbid - int(CBID_INCR),0))
        context['num_cookbooks'] = len(cookbooks)
        context['type']='view_all'
        context['message']="Displaying all cookbooks"
        
        print cookbooks
        return render_template("cookbooks_all.html",**context)
    if action == 'view':
        # This is to see the list of cookbooks
        cookbooks = []
        cmd = 'SELECT c.cbid, c.description FROM cookbooks as c, cookbookowners as cbo WHERE c.cbid=cbo.cbid AND cbo.userid=:userid ORDER BY c.cbid LIMIT :cbid_incr OFFSET :offset_value'
        cursor = g.conn.execute(text(cmd),offset_value=str(init_cbid),userid=userid,cbid_incr=CBID_INCR);
        for record in cursor:
            cookbooks.append((record['cbid'],record['description']))
        context['cookbooks'] = cookbooks
        context['userid']=str(userid)
        context['curr_cbid'] = str(init_cbid)
        context['next_cbid'] = str(init_cbid + int(CBID_INCR))
        context['prev_cbid'] = str(max(init_cbid - int(CBID_INCR),0))
        context['num_cookbooks'] = len(cookbooks)
        context['type']='view'
        context['message']="Displaying your cookbooks"
        print cookbooks
        return render_template("cookbooks.html",**context)
    else:
        return redirect('/users/'+str(userid)+'/cookbooks/<action>/<cbid>')
 
@app.route('/users/<userid>/cookbook/<action>')
@app.route('/users/<userid>/cookbook/<action>/<cbid>') 
def cookbook(userid,action,cbid=None):
    if action == 'add':
        cmd = 'SELECT recid, recipename FROM recipes'
        cursor = g.conn.execute(text(cmd));
        recipes = []
        for record in cursor:
            recipes.append((record['recid'],record['recipename']))
        context = dict(recipes = recipes)
        context['userid']=str(userid)
        return render_template("in_progress.html")
    elif action == 'view':
        return render_template("in_progress.html")
    else:
        return render_template("in_progress.html")





if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
