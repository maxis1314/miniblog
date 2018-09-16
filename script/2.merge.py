# coding=utf-8            
import re          
import os  
import sys
import codecs
import shutil
 
def merge_file():
    path = "fenci_output\\"
    resName = "result_all.txt"
    if os.path.exists(resName):
        os.remove(resName)
    result = codecs.open(resName, 'w', 'utf-8')
 
    num = 1
    while num <= 204:
        name = "%04d" % num 
        fileName = path + str(name) + ".txt"
        
        if not os.path.exists(fileName):
            break
        #print name
        
        source = open(fileName, 'r')
        line = source.readline()
        line = line.strip('\n')
        line = line.strip('\r')
 
        while line!="":
            line = unicode(line, "utf-8")
            line = line.replace('\n',' ')
            line = line.replace('\r',' ')
            result.write(line+ ' ')
            line = source.readline()
        else:
            #print 'End file: ' + str(num)
            result.write('\r\n')
            source.close()
        num = num + 1
        
    else:
        print 'End All'
        result.close()    
 
if __name__ == '__main__':
    merge_file()