import os
import unittest

import sys
sys.path.append('../')

from minitwit import app

from lib.FileDB import *
from lib.MessageDB import *
from lib.ConfigDB import *
from lib.Utils import *
import codecs

class TestCase(unittest.TestCase):
    def setUp(self):        
        self.app = app.test_client()

    def tearDown(self):
        pass
        
    def test_avatar(self):
        db = MessageDB(path='../data/test.json')
        messages = db.search_user_timeline_messages('admin','')


if __name__ == '__main__':
    unittest.main()