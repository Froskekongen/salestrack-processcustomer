#!/usr/bin/python3
# -*- coding: utf-8 -*-
import parse_postnummer
import csv
import frafalltm
import numpy as np
from sklearn.linear_model import LogisticRegression
from collections import Counter
from sklearn import metrics
import datetime

import plotly.plotly as py
import plotly.graph_objs as go
import sys



if __name__ == "__main__":
    notafter=datetime.datetime(2014,10,1)
    print(notafter)
    parsePost=parse_postnummer.ParsePostnummer()
    avisKategorier=parse_postnummer.ParseAvisKategori()


    with open('../data/qlik_tmsales.csv') as ff:
        spamreader = csv.reader(ff, delimiter=',', quotechar='"')
        aviser=set()
        featDictList=[]
        predDictList=[]
        maanedKjopt=np.zeros(12)

        stopcounter=0

        for iii,row in enumerate(spamreader):
            if iii==0:
                heads=row
                row=[(iii,r) for r in enumerate(row)]


            if iii>2:
                if row[11]=='G: 100 %':
                    continue
                featDict,predDict=frafalltm.parse_row(row,heads,parsePost.pn_to_navn)
                #if (row[0]>notafter) and ('Termin_12' in featDict):
                    #print(row[0],notafter,row[19])
                #    continue
                featDictList.append(featDict)
                predDictList.append(predDict)
                maanedKjopt[int(row[0].month)-1]+=1



                aviser.add(row[6])
                if row[2]=='Final stop':
                    stopcounter+=1
                elif (row[2]!='Final stop') and (row[2]!='-'):
                    row2Int=int(row[2])
                    if row2Int>=20:
                        stopcounter+=1

    print(stopcounter)
    maaned=['Januar','Februar','Mars','April','Mai','Juni','Juli','August',\
        'September','Oktober','November','Desember']

    # plotlydata=[go.Bar(x=maaned,y=maanedKjopt)]
    # plotlyMaaned={'data':plotlydata,'layout':{'title':'TM-salg per måned'}}
    # print(plotlydata)
    # py.plot(plotlyMaaned,filename='TMSALES_NOV2015',privacy='private')
    #sys.exit(1)


    avisDict=frafalltm.make_avis_dict(aviser,featDictList,predDictList)
    logRegParams={'n_jobs':-1,'class_weight':'balanced','penalty':'l1','C':0.5}
    classifier=LogisticRegression
    topCoeffsAvis={}
    toPred='CPO'
    for avis in avisDict.keys():
        if avis=='TOTAL':
            continue

        print(avis,'er i veiklasse',avisKategorier.avisVeiklasse(avis))
        frafalltm.trainAvis(avis,avisDict,topCoeffsAvis,classifier,logRegParams,toPred)
    #frafalltm.trainAvis('TOTAL',avisDict,topCoeffsAvis,classifier,logRegParams,'CPO')


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


    minVal=3
    delFeats=[]
    for feat,count in bestFeats.items():
        if count<minVal:
            delFeats.append(feat)
    for feat in delFeats:
        del bestFeats[feat]
    delFeats=[]
    for feat,count in worstFeats.items():
        if count<minVal:
            delFeats.append(feat)
    for feat in delFeats:
        del worstFeats[feat]
    print(bestFeats)
    print(worstFeats)

    xx,yy=[],[]
    for feat,val in bestFeats.items():
        feat=feat.replace('Rabattgruppe_','')
        feat=feat.replace('maaned','M')
        feat=feat.replace('Start = Første start_','')
        xx.append(feat)
        yy.append(val)

    xx1=[x for (y,x) in sorted(zip(yy,xx))]
    yy1=[y for (y,x) in sorted(zip(yy,xx))]

    plotlydata=[go.Bar(x=xx1,y=yy1)]
    plotlyMaaned={'data':plotlydata,'layout':{'title':'Variabler som har positiv innvirkning'}}
    py.plot(plotlyMaaned,filename='negativ-TM_'+toPred,privacy='private')


    #print(maanedKjopt)

    # checkVal='maaned_2'
    # for avis,val in topCoeffsAvis.items():
    #     dd=dict(val)
    #     if checkVal in dd:
    #         print(avis,checkVal,dd[checkVal])

    # traces=[]
    # for avis,vals in avisDict.items():
    #
    #     if avisKategorier.veiKlasseAvis(5,avis):
    #     #if avis =='ROMERIKES BLAD':
    #         clfProps=vals[-1]
    #         clData=go.Scatter(x=clfProps['roc_curve'][0],y=clfProps['roc_curve'][1],mode='lines',name=avis)
    #         print(clData)
    #         traces.append(  clData  )
    #
    # traces.append(go.Scatter(x=[0,1],y=[0,1],mode='dash',name='Ingen effekt'))
    #
    # py.plot(traces,filename='roc_curves_vei5')
