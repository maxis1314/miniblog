# -*- coding: utf-8 -*-
import json
from werkzeug import check_password_hash, generate_password_hash
from .FileDB import *
from .CommonDB import *
PER_PAGE = 10


class ConfigDB(CommonDB):
    def __init__( self,table='config', path=None ):
        CommonDB.__init__(self,table=table,path=path)
        
    def add_table(self,table):
        self.r.sadd('tables',table)
    def get_tables(self):
        return self.r.get('tables')
    def get_current(self):
        current = self.r.get('current')
        if not current:
            current = 'default'
        return current
    def set_current(self,table):
        self.r.set('current',table)
        
        
    def get_user(self,user_id):
        """Get user by username."""
        return self.r.hgetall('user:%s' % user_id)

    def add_user(self,username, email, password):
        """Add user with the specified credentials."""
        user_id = 'user:%s' % username
        self.r.hset(user_id, 'username', username)
        self.r.hset(user_id, 'email', email)
        self.r.hset(user_id, 'pw_hash',
               generate_password_hash(password))
    