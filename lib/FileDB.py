# -*- coding: utf-8 -*-
import json
import time
import os

class FileDB():
    file=None
    data={}
    auto_save=True
    def __init__( self, path ):  
        self.file = path
        self.loadjson()
    def loadjson(self):
        if os.path.exists(self.file):
            self.data = json.loads(open(self.file).read( ))
        else:
            self.data={}
        pass
    def save2file(self,file,content):
        file = open(file, 'w')
        file.write(content)
        file.close()
    def set_auto(self,flag):
        self.auto_save=flag
    def savejson(self):
        if self.auto_save:
            self.commit()
    def commit(self):      
        ymd = time.strftime("%Y-%m-%d", time.localtime()) 
        self.save2file(self.file,json.dumps(self.data,encoding="utf-8", indent=4, separators=(',', ': ')))
        self.save2file(self.file+"."+ymd+".json",json.dumps(self.data,encoding="utf-8", indent=4, separators=(',', ': ')))
    def hset(self,row,key,value):
        if not row in self.data:
            self.data[row]={}
        self.data[row][key]=value
        self.savejson()
    def set(self,row,value):        
        self.data[row]=value
        self.savejson()
    def get(self,row,default=None):        
        if row in self.data:
            return self.data[row]
        else:
            return default
    def hgetall(self,row):
        if not row in self.data:
            return {}
        else:
            return self.data[row]
    def hreset(self,row):
        self.data[row] = {}
        self.savejson()
    def areset(self,row):
        self.data[row] = []
        self.savejson()
    def lrange(self,row,start,len):
        if not row in self.data:
            return []
        return self.data[row][start:start+len]
    def len(self,row):
        if not row in self.data:
            return 0
        return len(self.data[row])
    def lpush(self,row,value):
        if not row in self.data:
            self.data[row]=[]
        self.data[row].insert(0,value)
        self.savejson()

    def ltrim(self,*args):
        pass
    def incr(self,row):
        if not row in self.data:
            self.data[row] = 1
        else:
            self.data[row]=self.data[row]+1
        return self.data[row]
    def remove(self,row):
        del self.data[row]
        self.savejson()
    def has(self,row):
        if row in self.data:
            return True
        else:
            return False
    def sismember(self,row,value):
        if not row in self.data:
            return False
        else:
            if value in self.data[row]:
                return True
            else:
                return False
       
    def sadd(self,row,value):
        if not row in self.data:
            self.data[row]=[]        
        if value in self.data[row]:
            return 
        else:
            self.data[row].append(value)
            self.savejson()
            
    def srem(self,row,value):
        if not row in self.data:
            self.data[row]=[]        
        if value in self.data[row]:
            self.data[row].remove(value)
            self.savejson()
    def flushdb(self):
        self.data={}
        self.savejson()
        
        
        