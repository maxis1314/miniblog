# -*- coding: utf-8 -*-

import os
import time
from hashlib import md5
from datetime import datetime
import json
from flask import Blueprint,Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
from werkzeug import check_password_hash, generate_password_hash
import redis
from jinja2 import TemplateNotFound

from lib.FileDB import *
from lib.MessageDB import *
from lib.ConfigDB import *
from lib.Utils import *
from lib import gl

memo_controller = Blueprint('memo', __name__, template_folder='templates')


@memo_controller.before_request
def before_request():
    """Make sure we are connected to the database each request and look
    up the current user so that we know he's there.
    """
    g.user = None
    if 'user_id' in session:
        g.user = gl.configdb.get_user(session['user_id'])
        gl.msgdb = MessageDB(session['table'])


@memo_controller.route('/', methods=['GET'])
def timeline():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    if not g.user:
        return redirect(url_for('memo.login'))
    page = int(request.args.get('page')) if request.args.get('page') else 0
    messages = gl.msgdb.get_user_timeline_messages(g.user['username'],page)
    count = gl.msgdb.get_user_timeline_messages_count(g.user['username'])

    metaDB = FileDB('data/ml.meta')
    table2num = metaDB.hgetall("table2num")
    cluster = metaDB.hgetall("cluster")      
    msgcluster = {}
    for (d,x) in table2num.items():
        msgcluster[d] = cluster[x] if x in cluster else 0    
    for msg in messages:        
        msg['cluster'] = msgcluster.get("%s:%d"%(session['table'],msg['id']),0)        
        keywords = metaDB.get("cluster:%s" % msg['cluster'],[])
        keywords.sort(key=lambda x:len(x))
        keywords2 = filter(lambda x: not filter_keword(x) , keywords)        
        msg['text'] = highlight_keywords(msg['text'],keywords2,['#90EE90','#FFE4C4','#ADFF2F'])

    return render_template2('timeline.html', messages=messages, page=page if page>=0 else 0, count=count)


@memo_controller.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    if not g.user:
        abort(401)
    return render_template2('timeline.html',
        messages=gl.msgdb.get_public_timeline_messages())

@memo_controller.route('/message/<id>')
def message(id):
    metaDB = FileDB('data/ml.meta')
    recomand = metaDB.get("recomand")  
    num2table = metaDB.get("num2table")
    table2num = metaDB.hgetall("table2num")
    
    mid = table2num.get('%s:%s'%(session['table'],id))
    print "mid=",mid
    
    near = []
    for (d,x) in recomand.items():
        arr = d.split(':')
        if arr[0] == mid:
            near.append([int(arr[1]),x])
    
    near = sorted(near, key=lambda x: -x[1]) 
    near = near[0:5]
    
    messages = gl.msgdb.get_messages([id])
    
    for item in near:
        str = num2table.get("%d"%item[0])
        arr = str.split(':')
        db = MessageDB(arr[0])
        messages_new = db.get_messages([int(arr[1])])    
        for msg in messages_new:
            msg['table'] = arr[0] + ":%f"%  item[1]
        messages = messages + messages_new
    
            
    return render_template2('timeline.html', messages=messages, page=0, count=1)
        
@memo_controller.route('/cluster/<id>')
def cluster(id):
    metaDB = FileDB('data/ml.meta')
    table2num = metaDB.hgetall("table2num")
    cluster = metaDB.hgetall("cluster")   
    keywords = metaDB.get("cluster:%s"%id)

    msgcluster = {}
    for (d,x) in table2num.items():
        msgcluster[d] = cluster[x] if x in cluster else 0
    
    matched={}
    for (d,x) in msgcluster.items():
        arr = d.split(':')
        if x == id:
            if not arr[0] in matched:
                matched[arr[0]]=[]
            matched[arr[0]].append(int(arr[1]))
    
    print matched
    messages=[]
    for (d,x) in matched.items():
        db = MessageDB(d)
        messages_new = db.get_messages(x)    
        for msg in messages_new:
            msg['table'] = d
        messages = messages + messages_new   
  
  
    keywords.sort(key=lambda x:len(x))
    keywords2 = filter(lambda x: not filter_keword(x) , keywords)
    colors = ['#FFB6C1','#FFC0CB','#DC143C','#FFF0F5','#DB7093','#FF69B4','#FF1493','#C71585','#DA70D6','#D8BFD8','#DDA0DD','#EE82EE','#FF00FF','#FF00FF','#8B008B','#BA55D3','#9400D3','#9932CC','#8A2BE2','#9370DB','#7B68EE','#6A5ACD','#483D8B','#E6E6FA','#F8F8FF','#0000FF','#4169E1','#6495ED','#B0C4DE','#778899','#708090','#1E90FF','#F0F8FF','#4682B4','#87CEFA','#87CEEB','#00BFFF','#ADD8E6','#B0E0E6','#5F9EA0','#F0FFFF','#E1FFFF','#AFEEEE','#00FFFF','#00FFFF','#00CED1','#008B8B','#008080','#48D1CC','#20B2AA','#40E0D0','#7FFFAA','#00FA9A','#F5FFFA','#00FF7F','#3CB371','#2E8B57','#F0FFF0','#90EE90','#98FB98','#8FBC8F','#32CD32','#00FF00','#228B22','#008000','#006400','#7FFF00','#7CFC00','#ADFF2F','#556B2F','#6B8E23','#FAFAD2','#FFFFF0','#FFFFE0','#FFFF00','#808000','#BDB76B','#FFFACD','#EEE8AA','#F0E68C','#FFD700','#FFF8DC','#DAA520','#FFFAF0','#FDF5E6','#F5DEB3','#FFE4B5','#FFA500','#FFEFD5','#FFEBCD','#FFDEAD','#FAEBD7','#D2B48C','#DEB887','#FFE4C4','#FF8C00','#FAF0E6','#CD853F','#FFDAB9','#F4A460','#D2691E','#8B4513','#FFF5EE','#A0522D','#FFA07A','#FF7F50','#FF4500','#E9967A','#FF6347','#FFE4E1','#FA8072','#FFFAFA','#F08080','#BC8F8F','#CD5C5C','#FF0000','#A52A2A','#B22222','#8B0000','#800000']
    
    
    for msg in messages:
        msg['cluster'] = id        
        msg['text'] = highlight_keywords(msg['text'],keywords2,colors)
        
    
    #for index, item in enumerate(keywords):
    #    k=index%len(colors)
    #    keywords[index] = '<p style="display:inline;background:%s;">%s</p>'%(colors[k],item)

            
    return render_template2('timeline.html', messages=messages, page=0, count=len(matched), keywords=keywords)

@memo_controller.route('/usertl/<username>')
def user_timeline(username):
    """Display's a users tweets."""
    user = gl.configdb.get_user(username)
    if not user:
        abort(404)
    followed = False
    if g.user:
        followed = gl.msgdb.is_following(session['user_id'], username)
    return render_template2('timeline.html',
                           messages=gl.msgdb.get_user_timeline_messages(username),
                           followed=followed,
                           profile_user=user)


@memo_controller.route('/usertl/<username>/follow')
def follow_user(username):
    """Adds the current user as follower of the given user."""
    if not g.user:
        abort(401)
    user = gl.msgdb.get_user(username)
    if not user:
        abort(404)
    gl.msgdb.follow(session['user_id'], username)
    flash('You are now following "%s"' % username)
    return redirect(url_for('memo.user_timeline', username=username))


@memo_controller.route('/usertl/<username>/unfollow')
def unfollow_user(username):
    """Removes the current user as follower of the given user."""
    if not g.user:
        abort(401)
    user = gl.msgdb.get_user(username)
    if not user:
        abort(404)
    gl.msgdb.unfollow(session['user_id'], username)
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('memo.user_timeline', username=username))


@memo_controller.route('/add_message', methods=['POST'])
def add_message():
    """Registers a new message for the user."""
    if 'user_id' not in session:
        abort(401)
        
    table = get_param('table')
    if table:
        session['table'] = table
        gl.configdb.set_current(table)
        #global gl.msgdb
        gl.msgdb = MessageDB(table)
    
    if request.form['text']:
        message_id = gl.msgdb.push_message(session['user_id'], request.form['text'])
        gl.msgdb.add_message_to_user_timeline(session['user_id'], message_id)
        gl.msgdb.add_message_to_public_timeline(message_id)
        flash('Your message was recorded')
    return redirect(url_for('memo.timeline'))
    
@memo_controller.route('/delete_message', methods=['GET'])
def delete_message():
    """Registers a new message for the user."""
    if 'user_id' not in session:
        abort(401)
    if request.args['msgid']:
        gl.msgdb.delete_user_message(session['user_id'],int(request.args.get('msgid')))        
        flash('Your message was deleted')
    if request.args.get('from') == 'public_timeline':
        return redirect(url_for('memo.public_timeline',page=request.args.get('page')))
    elif request.args.get('from') == 'user_timeline':
        return redirect(url_for('memo.user_timeline',username=request.args.get('user'),page=request.args.get('page')))
    else:
        return redirect(url_for('memo.timeline',page=request.args.get('page')))
        
        
@memo_controller.route('/select_notebook', methods=['POST'])
def select_notebook():
    """Registers a new message for the user."""
    if 'user_id' not in session:
        abort(401)
    table = get_param('text')
    newtable = get_param('newtable')
    if newtable:
        gl.configdb.add_table(newtable)
        table = newtable
    else:
        gl.configdb.reload()

    if table:
        session['table'] = table
        gl.configdb.set_current(table)
        #global gl.msgdb
        gl.msgdb = MessageDB(table)
 
    return redirect(url_for('memo.timeline'))
        

@memo_controller.route('/search_message', methods=['POST'])
def search_message():
    """Registers a new message for the user."""
    if 'user_id' not in session:
        abort(401)
        
    messages = gl.msgdb.search_user_timeline_messages(g.user['username'],request.form['text'])
    return render_template2('timeline.html', messages=messages,key=request.form['text'])
    
    

@memo_controller.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('memo.timeline'))
    error = None
    if request.method == 'POST':
        user = gl.configdb.get_user(request.form['username'])
        if not user:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user['username']
            session['table'] = gl.configdb.get_current()
            #global gl.msgdb
            gl.msgdb = MessageDB(session['table'])
            return redirect(url_for('memo.timeline'))
    return render_template2('login.html', error=error)


@memo_controller.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('memo.timeline'))
    #disable register
    if not g.user:
        abort(400)
        
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                 '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif gl.configdb.get_user(request.form['username']):
            error = 'The username is already taken'
        else:
            gl.configdb.add_user(request.form['username'],
                     'a@a.com',
                     request.form['password'])
            flash('You were successfully registered and can login now')
            return redirect(url_for('memo.login'))
    return render_template2('register.html', error=error)


@memo_controller.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    session.pop('table', None)
    return redirect(url_for('memo.login'))
