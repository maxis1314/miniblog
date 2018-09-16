# -*- coding: utf-8 -*-
import json
from datetime import datetime
from flask import request,render_template
import gl
import re
import time
global stat_func
stat_func={}


def highlight_keywords(text,keywords,colors):
    keywords.sort(key=lambda x:len(x))
    keywords2 = filter(lambda x: not filter_keword(x) , keywords)
    
    #colors = ['#FFB6C1','#FFC0CB','#DC143C','#FFF0F5','#DB7093','#FF69B4','#FF1493','#C71585','#DA70D6','#D8BFD8','#DDA0DD','#EE82EE','#FF00FF','#FF00FF','#8B008B','#BA55D3','#9400D3','#9932CC','#8A2BE2','#9370DB','#7B68EE','#6A5ACD','#483D8B','#E6E6FA','#F8F8FF','#0000FF','#4169E1','#6495ED','#B0C4DE','#778899','#708090','#1E90FF','#F0F8FF','#4682B4','#87CEFA','#87CEEB','#00BFFF','#ADD8E6','#B0E0E6','#5F9EA0','#F0FFFF','#E1FFFF','#AFEEEE','#00FFFF','#00FFFF','#00CED1','#008B8B','#008080','#48D1CC','#20B2AA','#40E0D0','#7FFFAA','#00FA9A','#F5FFFA','#00FF7F','#3CB371','#2E8B57','#F0FFF0','#90EE90','#98FB98','#8FBC8F','#32CD32','#00FF00','#228B22','#008000','#006400','#7FFF00','#7CFC00','#ADFF2F','#556B2F','#6B8E23','#FAFAD2','#FFFFF0','#FFFFE0','#FFFF00','#808000','#BDB76B','#FFFACD','#EEE8AA','#F0E68C','#FFD700','#FFF8DC','#DAA520','#FFFAF0','#FDF5E6','#F5DEB3','#FFE4B5','#FFA500','#FFEFD5','#FFEBCD','#FFDEAD','#FAEBD7','#D2B48C','#DEB887','#FFE4C4','#FF8C00','#FAF0E6','#CD853F','#FFDAB9','#F4A460','#D2691E','#8B4513','#FFF5EE','#A0522D','#FFA07A','#FF7F50','#FF4500','#E9967A','#FF6347','#FFE4E1','#FA8072','#FFFAFA','#F08080','#BC8F8F','#CD5C5C','#FF0000','#A52A2A','#B22222','#8B0000','#800000']
    
    j=1    
    for key in keywords2:
        k=j%len(colors)
        text = text.replace(key,'<p style="display:inline;background:%s;">%s</p>'%(colors[k],key))
        j=j+1
    return text

def filter_keword(s):
    return (len(s)<=5 and re.match( r'^[a-zA-Z0-9]+$', s, re.M|re.I)) or is_number(s) or s in ["inline","color","background","style","display"]

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

def render_template2(file,**args):
    args['tables'] = gl.configdb.get_tables()
    if not 'page' in args:
        args['page'] = 0
    return render_template(file,**args)



def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(float(timestamp)).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return None#'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        #(md5(email.strip().lower().encode('utf-8')).hexdigest(), size)
        
        
def get_param(name):
    if name in request.form:
        return request.form[name]
    return request.args.get(name)
    
    
def timeme(fn):    
    def wrapper(*args, **kwargs):
        start_time=time.time()
        
        result = fn(*args, **kwargs)
        
        cost = time.time()-start_time
        print ("%s cost %f" % (fn.__name__ ,cost))
        
        if fn.__name__ in stat_func:
            stat_func[fn.__name__]['count']+=1
            stat_func[fn.__name__]['time']+=cost
        else:
            stat_func[fn.__name__]={}
            stat_func[fn.__name__]['count']=1
            stat_func[fn.__name__]['time']=cost


        return result
    return wrapper