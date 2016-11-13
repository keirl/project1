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

def validate_userid(userid):
    cmd = 'SELECT userid FROM users WHERE userid=:userid'
    cursor = g.conn.execute(text(cmd),userid=userid);
    record = cursor.fetchone()
    
def average_rating(recid):
    try:
        cmd = 'SELECT AVG(rating) AS average_rating FROM reciperatings WHERE recid=:recid'
        cursor = g.conn.execute(text(cmd),recid=recid);
        record = cursor.fetchone()
        return_val = str(round(record['average_rating'],1))
        cursor.close()
        return return_val
    except:
        cursor.close()
        return None
    

def user_rating(recid, userid):
    try:
        cmd = 'SELECT rating FROM reciperatings WHERE recid=:recid AND userid=:userid'
        cursor = g.conn.execute(text(cmd),recid=recid, userid=userid);
        record = cursor.fetchone()
        return_val = str(record['rating'])
        cursor.close()
        return return_val
    except:
        cursor.close()
        return '0'
        
def categories_str(recid):
    cmd = 'SELECT name FROM recipecategories WHERE recid=:recid'
    cursor = g.conn.execute(text(cmd),recid=recid);
    categories = []
    for record in cursor:
        categories.append(record['name'])
    cursor.close
    return ', '.join(categories)
    

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
    cursor.close()
    userid = record['userid']
    return redirect('/users/'+str(userid))    
        
     
@app.route('/users/<userid>/cookbooks/view', methods=['GET'])
@app.route('/users/<userid>/cookbooks/view/<cbidx>') 
def cookbooks_view(userid,cbidx=None):
     # This is to see the list of cookbooks
    context = {}
    CBIDX_INCR = 10                   

    if cbidx is None:
        init_cbidx = 0
    elif int(cbidx) >= 0:
        init_cbidx = int(cbidx)
    else:
        init_cbidx = 0
   
    cmd = 'SELECT c.cbid as cbid, c.description as description \
        FROM cookbooks as c, cookbookowners as cbo \
        WHERE c.cbid=cbo.cbid AND cbo.userid=:userid \
        ORDER BY c.cbid'
    cursor = g.conn.execute(text(cmd),userid=userid)
    cookbooks_owned = []
    for record in cursor:
        cookbooks_owned.append((record['cbid'],record['description']))
    cursor.close()
    context['cookbooks_owned'] = cookbooks_owned    
    
    cmd = 'SELECT c.cbid AS cb, c.description AS d FROM cookbooks AS c \
        WHERE c.cbid NOT IN \
            (SELECT cbo.cbid FROM cookbookowners AS cbo WHERE userid=:userid) \
        ORDER BY c.cbid LIMIT :cbidx_incr OFFSET :offset_value '
    cursor = g.conn.execute(text(cmd),offset_value=int(init_cbidx),cbidx_incr=CBIDX_INCR,userid=userid);
    cookbooks = []
    for record in cursor:
        cookbooks.append((record['cb'],record['d']))
    cursor.close()
    context['cookbooks'] = cookbooks
        
    context['userid']=str(userid)
    context['curr_idx'] = str(init_cbidx)
    context['next_idx'] = str(init_cbidx + CBIDX_INCR)
    context['prev_idx'] = str(max(init_cbidx - CBIDX_INCR,0))
        
    print cookbooks
    return render_template("cookbooks.html",**context)
    
@app.route('/users/<userid>/cookbooks/add/<curr_idx>', methods=['POST'])
def cookbooks_add(userid,curr_idx=0):
    for cbid in request.form:
        print cbid
        cmd = 'INSERT INTO cookbookowners (cbid, userid) VALUES (:cbid, :userid)'
        ## Add integrity checking
        g.conn.execute(text(cmd), cbid = int(cbid), userid = int(userid));
    return redirect('/users/'+str(userid)+'/cookbooks/view/'+curr_idx)
    
@app.route('/users/<userid>/cookbooks/remove/<curr_idx>', methods=['POST'])
def cookbooks_remove(userid,curr_idx=0):
    for cbid in request.form:
        print cbid
        cmd = 'DELETE FROM cookbookowners WHERE cbid=:cbid AND userid=:userid'
        ## Add integrity checking
        g.conn.execute(text(cmd), cbid = int(cbid), userid = int(userid));
    return redirect('/users/'+str(userid)+'/cookbooks/view/'+curr_idx)

@app.route('/users/<userid>/cookbook/view/<cbid>')
@app.route('/users/<userid>/cookbook/view/<cbid>/<recidx>') 
def cookbook_view(userid,cbid,recidx=0):
    RECIDX_INCR = 10
    
    # Check recidx
    if int(recidx) >= 0:
        init_recidx = int(recidx)
    else:
        init_recidx = 0
    
    context={}
    
    # Get recipes in cookbook
    cmd = 'SELECT r.recid AS recid, r.recipename AS recipename \
        FROM cookbookcontents AS cc, recipes AS r \
        WHERE cc.cbid=:cbid AND cc.recid=r.recid'
    cursor = g.conn.execute(text(cmd),cbid=cbid);
    recipes_in_cb = []
    for record in cursor:
        recipes_in_cb.append((record['recid'],record['recipename']))
    cursor.close()
    context['recipes_in_cb'] = recipes_in_cb
    
    print recipes_in_cb
    
    # Get categories, average ratings, your rating
    
    # Get recipes not in cookbook
    cmd = 'SELECT r.recid AS recid, r.recipename AS recipename \
        FROM recipes AS r \
        WHERE r.recid NOT IN \
            (SELECT cc.recid  FROM cookbookcontents AS cc WHERE cc.cbid=:cbid) \
        ORDER BY r.recid LIMIT :recidx_incr OFFSET :recidx'
    cursor = g.conn.execute(text(cmd),cbid=cbid,recidx_incr=RECIDX_INCR,recidx=init_recidx);
    recipes_not_in_cb = []
    for record in cursor:
        recipes_not_in_cb.append((record['recid'],record['recipename']))
    cursor.close()
    
    print recipes_not_in_cb
    context['recipes_not_in_cb'] = recipes_not_in_cb
    # Get categories and ratings
    
    # Get name of cookbook
    cmd = 'SELECT description FROM cookbooks WHERE cbid=:cbid'
    cursor = g.conn.execute(text(cmd),cbid=cbid);
    temp=cursor.fetchone()
    context['cbname'] = temp['description']
    context['cbid'] = cbid
    print context['cbname']
    cursor.close()
    
    context['userid']=str(userid)
    context['curr_idx'] = str(init_recidx)
    context['next_idx'] = str(init_recidx + RECIDX_INCR)
    context['prev_idx'] = str(max(init_recidx - RECIDX_INCR,0))
    
    return render_template("cookbook.html",**context)

@app.route('/users/<userid>/cookbook/add/<cbid>', methods=['POST'])
@app.route('/users/<userid>/cookbook/add/<cbid>/<curr_idx>', methods=['POST'])
def cookbook_add(userid,cbid,curr_idx=0):
    for recid in request.form:
        print recid
        cmd = 'INSERT INTO cookbookcontents (cbid, recid) VALUES (:cbid, :recid)'
        ## Add integrity checking
        g.conn.execute(text(cmd), cbid = int(cbid), recid = int(recid));
    return redirect('/users/'+str(userid)+'/cookbook/view/'+cbid+'/'+str(curr_idx))

@app.route('/users/<userid>/cookbook/remove/<cbid>', methods=['POST'])    
@app.route('/users/<userid>/cookbook/remove/<cbid>/<curr_idx>', methods=['POST'])
def cookbook_remove(userid,cbid,curr_idx=0):
    for recid in request.form:
        print recid
        cmd = 'DELETE FROM cookbookcontents WHERE cbid=:cbid AND recid=:recid'
        ## Add integrity checking
        g.conn.execute(text(cmd), cbid = int(cbid), recid = int(recid));
    return redirect('/users/'+str(userid)+'/cookbook/view/'+cbid+'/'+str(curr_idx))

@app.route('/users/<userid>/cookbook/new')
def cookbook_new(userid):
    context = {}
    context['userid']=userid
    return render_template('cookbook_new.html',**context) 
    
@app.route('/users/<userid>/cookbook/add_new', methods=['POST'])
def cookbook_add_new(userid):
    new_cb = request.form['name']
    print new_cb
    cmd = 'INSERT INTO cookbooks (description) VALUES (:new_cb) RETURNING cbid'
    cursor = g.conn.execute(text(cmd), new_cb=new_cb);
    temp=cursor.fetchone()
    cbid = temp['cbid']
    return redirect('/users/'+str(userid)+'/cookbook/view/'+str(cbid))
    
@app.route('/users/<userid>/recipes/view')
@app.route('/users/<userid>/recipes/view/<recidx>')
def recipes_view(userid,recidx=0):

    RECIDX_INCR = 20
    
    # Check recidx
    if int(recidx) >= 0:
        init_recidx = int(recidx)
    else:
        init_recidx = 0
    
    context={}
   
    cmd = 'SELECT recid, recipename FROM recipes \
        ORDER BY recid LIMIT :recidx_incr OFFSET :recidx'
    cursor = g.conn.execute(text(cmd),recidx_incr=RECIDX_INCR,recidx=init_recidx);
    recipes = []
    for record in cursor:
        recipes.append((record['recid'],record['recipename']))
    cursor.close()
    
    print recipes
    context['recipes'] = recipes
    
    
    context['userid']=str(userid)
    context['curr_idx'] = str(init_recidx)
    context['next_idx'] = str(init_recidx + RECIDX_INCR)
    context['prev_idx'] = str(max(init_recidx - RECIDX_INCR,0))
        
    return render_template("recipes.html",**context)



@app.route('/users/<userid>/recipe/view/<recid>')
def recipe_view(userid,recid):
    context={}
   
    cmd = 'SELECT recipename, directions, author, url FROM recipes WHERE recid=:recid'
    cursor = g.conn.execute(text(cmd),recid=recid);
    record = cursor.fetchone()
    context['recipename']=record['recipename']
    context['directions']=record['directions']
    context['author']=record['author']
    context['url']=record['url']
    cursor.close()
    
    cmd = 'SELECT rc.quantity AS quantity, rc.optional AS optional, rc.prep AS prep, i.shortname AS shortname \
        FROM ingredients AS i, recipescontain AS rc WHERE i.ingid=rc.ingid AND rc.recid=:recid'   
    cursor = g.conn.execute(text(cmd),recid=recid);
    ingredients = []
    for record in cursor:
        ingredients.append((record['quantity'],str(record['optional']),record['prep'],record['shortname']))
    cursor.close()

    context['average_rating'] = average_rating(recid)
    context['your_rating']=user_rating(recid,userid)
    context['categories_str']=categories_str(recid)
    
    context['ingredients'] = ingredients
    context['recid'] = recid
    context['userid']=str(userid)
    
    return render_template("recipe.html",**context)
    
@app.route('/users/<userid>/recipe/update_rating/<recid>')
def recipe_update_rating(userid,recid):
    rating = request.form['rating']
    try:
        cmd = 'INSERT INTO reciperatings (recid, userid, rating) VALUES (:recid, :userid, :rating)'
        g.conn.execute(text(cmd),recid=recid, userid=userid, rating=rating);
    except IntegrityError:
        try:
            cmd = 'UPDATE reciperatings SET rating:rating WHERE recid=:recid AND userid=:userid'
            g.conn.execute(text(cmd),recid=recid, userid=userid, rating=rating);
        except:
            return redirect('/')
    except:
        return redirect('/')
    
    return redirect('in_progress.html')

@app.route('/users/<userid>/recipe/update_categories/<recid>')
def recipe_update_categories(userid,recid):
    return redirect('in_progress.html')
    
@app.route('/users/<userid>/recipe/new')
def recipe_update_categories2(userid,recid):
    return redirect('in_progress.html')
    
@app.route('/users/<userid>/recipe/new_add')
def recipe_update_categories3(userid,recid):
    return redirect('in_progress.html')


@app.route('/users/<userid>/pantries/view/')
def pantry_view(userid):
    context={}
   
    cmd = 'SELECT location FROM pantries LEFT JOIN users on users.userid=pantries.userid where users.userid=:userid;'
    cursor = g.conn.execute(text(cmd),userid=userid);
    record = cursor.fetchone()
    pantries_owned = []
    for record in cursor:
        pantries_owned.append(record['location'])
    #context['location']=record['location']
    #context['url']=record['url']
    cursor.close()
    
    context['pantries_owned'] = pantries_owned    
    return render_template("pantries.html",**context)

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
