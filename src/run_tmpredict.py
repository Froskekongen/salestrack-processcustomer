#!/usr/bin/python3
# -*- coding: utf-8 -*-
import parse_postnummer
import csv
import frafalltm
import numpy as np
from sklearn.linear_model import LogisticRegression
from collections import Counter



if __name__ == "__main__":
    parsePost=parse_postnummer.ParsePostnummer()
    with open('../data/qlik_tmsales.csv') as ff:
        spamreader = csv.reader(ff, delimiter=',', quotechar='"')
        aviser=set()
        featDictList=[]
        churned=[]
        abo_lengde=[]
        for iii,row in enumerate(spamreader):
            if iii==0:
                heads=row
                row=[(iii,r) for r in enumerate(row)]
            if iii>2:
                if row[11]=='G: 100 %':
                    continue
                featDict,predDict=frafalltm.parse_row(row,heads,parsePost.pn_to_navn)
                featDictList.append(featDict)
                churned.append(predDict['aktiv'])
                abo_lengde.append(predDict['lengde'])
                aviser.add(row[6])
    # with open('/mnt/tmsales/aviser.csv',mode='w') as ff:
    #     for avis in aviser:
    #         ff.write(avis+'\n')

    churned=np.array(churned)
    abo_lengde=np.array(abo_lengde)

    avisDict=frafalltm.make_avis_dict(aviser,featDictList,churned,abo_lengde)
    logRegParams={'n_jobs':-1,'class_weight':'balanced','penalty':'l1','C':0.5}
    classifier=LogisticRegression
    topCoeffsAvis=frafalltm.trainAvis(avisDict,classifier,logRegParams)


    bestFeats=Counter()
    worstFeats=Counter()
    for avis,val in topCoeffsAvis.items():
        for feat,val2 in val:
            if val2>0.3:
                bestFeats[feat]+=1
            if val2<0.3:
                worstFeats[feat]+=1
        print(avis)
        print(val)
        print('------------------')
    print(bestFeats)
    print(worstFeats)
