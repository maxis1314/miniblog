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
##############################################
# Configuration
REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
DEBUG = True
SECRET_KEY = 'development key'

# Create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)

gl.msgdb = None
gl.configdb = ConfigDB()


@app.route('/post/', defaults={'post_id': 6})
@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id

#################################################



# Add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url


if __name__ == '__main__':
    from controller.admin import admin_controller
    app.register_blueprint(admin_controller)
    from controller.memo import memo_controller
    app.register_blueprint(memo_controller)
    
    app.run(debug=True,host='0.0.0.0')
