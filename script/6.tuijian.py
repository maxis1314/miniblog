# coding=utf-8  
import os  
import sys
import codecs
import numpy as np 
import pandas as pd
sys.path.append('../')
from lib.FileDB import *


def cosSimilar(inA,inB):
    inA=np.mat(inA)
    inB=np.mat(inB)
    num=float(inA*inB.T)
    denom=np.linalg.norm(inA)*np.linalg.norm(inB)
    if denom == 0:
        denom=0.000001
    return 0.5+0.5*(num/denom)
    
    
print cosSimilar([1,0],[1,1])

import pandas as pd
data = pd.read_table('tfidf_result_all.txt',encoding='utf8',delim_whitespace=True)

#print data.loc[1].tolist()

shape=data.shape
print shape


testdb = FileDB('../data/ml.meta')
testdb.set_auto(False)
testdb.hreset("recomand")

for i in range(0,shape[0]):    
    for j in range(0,shape[0]):
        sim = cosSimilar(data.loc[i].tolist(),data.loc[j].tolist())
        if sim > 0.5 and sim<1:
            testdb.hset("recomand","%d:%d"%(i,j),sim)
            testdb.hset("recomand","%d:%d"%(j,i),sim)
testdb.commit()            
            