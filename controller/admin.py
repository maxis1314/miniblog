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
import codecs


admin_controller = Blueprint('admin', __name__, template_folder='templates', url_prefix='/admin/')


@admin_controller.route('/')
def index():
    try:
        return render_template('admin/index.html')
    except TemplateNotFound:
        abort(404)
        
@admin_controller.route('/genfile', methods=['GET', 'POST'])
def genfile():
    tables = gl.configdb.get_tables()
    testdb = FileDB('data/ml.meta')
    testdb.hreset('num2table')
    testdb.hreset('table2num')
    num = 1
    for table in tables:
        db = MessageDB(table)
        messages = db.search_user_timeline_messages('admin','')
        for msg in messages:
            name = "%04d" % num
            
            testdb.hset('num2table',"%d"%num,table+":%s"%msg['id'])
            testdb.hset('table2num',table+":%s"%msg['id'],"%d"%num)
            fileName = "script/fenci_input/" + str(name) + ".txt"            
            result = codecs.open(fileName, 'w', 'utf-8')
            line = msg['text']
            line = line.replace('\n',' ')
            line = line.replace('\r',' ')
            result.write(line)
            result.close()
            num = num + 1
    return render_template('info.html',info='success')
        

