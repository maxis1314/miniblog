#encoding=utf-8
import sys
sys.path.append('../')
from lib.FileDB import *
from lib.MessageDB import *
from lib.ConfigDB import *
from lib.Utils import *
import codecs

configdb = ConfigDB(path="../data/config.json")

tables = configdb.get_tables()

testdb = FileDB('../data/ml.meta')
testdb.hreset('num2table')
testdb.hreset('table2num')
num = 1
for table in tables:
    db = MessageDB(path='../data/%s.json'%table)
    messages = db.search_user_timeline_messages('admin','')
    for msg in messages:
        name = "%04d" % num
        
        testdb.hset('num2table',"%d"%num,table+":%s"%msg['id'])
        testdb.hset('table2num',table+":%s"%msg['id'],"%d"%num)
        fileName = "fenci_input/" + str(name) + ".txt"            
        result = codecs.open(fileName, 'w', 'utf-8')
        line = msg['text']
        line = line.replace('\n',' ')
        line = line.replace('\r',' ')
        result.write(line)
        result.close()
        num = num + 1