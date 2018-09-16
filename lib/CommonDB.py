# -*- coding: utf-8 -*-
import json
from werkzeug import check_password_hash, generate_password_hash
from .FileDB import *
PER_PAGE = 10


class CommonDB(object):
    table="b"
    r=None
    def __init__( self, table=None, path=None ):
        if not path:
            self.table = table
            path = 'data/%s.json' % self.table
        print path
        self.r = FileDB(path)       

    def flushdb(self):
        self.r.flushdb()
        
    def reload(self):
        self.r.loadjson()