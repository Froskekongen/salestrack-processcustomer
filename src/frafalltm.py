#!/usr/bin/python3
# -*- coding: utf-8 -*-

from collections import defaultdict,Counter
from sklearn.feature_extraction import DictVectorizer
from sklearn.decomposition import TruncatedSVD,NMF
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import StratifiedKFold,train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import Normalizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
from sklearn.preprocessing import Imputer
from sklearn import metrics
from sklearn import preprocessing
import csv
import datetime
import numpy as np


def custCPO(cust_type,scenario):
    nykundecpo=[552,879,1131]
    pkundecpo=[454,577,844]
    if cust_type=='RESTART':
        return pkundecpo[scenario]
    else:
        return nykundecpo[scenario]

def sub_has_value(sublength,prodprice,normalprice,termin,customercpo):
    """
    Easy calculation that says whether a customer is valuable or not.
    """

    if (termin==12) and (sublength>2):
        if prodprice>customercpo:
            return 1
        else:
            return 0
    elif (termin==12) and (sublength<=2):
        return 0
    else:
        betalt=0
        #antallTerminer=sublength/termin
        #overTermin=(antallTerminer%1.)*termin
        tt=sublength
        if tt>1.5:
            betalt=prodprice
        tt-=termin
        ncost=prodprice
        while tt>termin:
            if tt>1.5:
                #print(betalt,tt)
                ncost=(ncost+normalprice)/2
                betalt+=ncost
            tt-=termin
        #print(betalt)
    if betalt>customercpo:
        return 1
    else:
        return 0

def custHasValscen(cust_type,sublength,prodprice,normalprice,termin):
    hval=[]
    for iii in range(3):
        cpo=custCPO(cust_type,iii)
        hasVal=sub_has_value(sublength,prodprice,normalprice,termin,cpo)
        hval.append(hasVal)
    return hval






def parse_row(rr,heads,pn_parser):
    predDict={}
    featDict={}
    def parseDate(tt):
        ret=tt
        try:
            ret=datetime.datetime.strptime(tt,'%d.%m.%Y')
        except Exception as _:
            pass
        return ret

    oneHotInds=[3,6,8,9,11,15,19] # 6 tittel, 7 produkt, 14 er kampanjekode,
        #13 er tilbudskode, 16 er postnummer 10 er database
    oneHotList=[heads[ind]+'_'+str(rr[ind]) for ind in oneHotInds]
    try:
        oneHotList.append( pn_parser[int(rr[16])] ) #postnummer
    except Exception as e:
        print('Exception, postnummer:',e)

    dateInds=[0,1,12]
    for ind in dateInds:
        rr[ind]=parseDate(rr[ind])

    ## Customer churn and (current) length of subscription
    if rr[1]!='Aktiv':
        length_of_subs=(rr[1]-rr[0]).days/30.4 #length in months
        ppsalg=float(rr[17].replace(',','.'))
        npris=float(rr[18].replace(',','.'))
        cType=rr[3]
        termin=float(rr[19])
        hval=custHasValscen(cType,length_of_subs,ppsalg,npris,termin)
        #print(cType,length_of_subs,length_of_subs*30.4,ppsalg,npris,termin)
        #print(hval)
        #print(predDict)
        predDict['CPO']=hval
        #input()

    if rr[1]=='Aktiv':
        predDict['churned']=0
        predDict['lengde']=5000 #impute. Not good imputing. For
        predDict['CPO']=[1,1,1]
    else:
        predDict['churned']=1
        predDict['lengde']=length_of_subs


    ## Getting age (in days)
    try:
        alder=float((rr[0]-rr[12]).days)
    except Exception as _:
        alder=float('nan')
    featDict['alder']=alder

    ## Restart or new customer
    if (rr[4]=='First event') and (rr[3]=='RESTART'):
        siden_sist=float(800)
    elif rr[3]=='RESTART':
        siden_sist=int(rr[4])
    else:
        siden_sist=0.
        oneHotList.append('NY_KUNDE')
    featDict['siden_sist']=siden_sist

    oneHotList.append('maaned_'+str(rr[0].month))

    for dd in oneHotList:
        featDict[dd]=1.

    return featDict,predDict




def make_avis_dict(aviser,featDictList,predDictList):
    avisDict={}
    featDictListTotal=[]
    predTotalCreated=False
    for avis in aviser:
        if not avis:
            continue
        kk='Avis_'+avis
        featDictList2=[feats for feats in featDictList if kk in feats]
        predDictList2=[preds for preds,feats in zip(predDictList,featDictList) if kk in feats]
        # if len(featDictList2)<50:
        #     continue

        predDict=defaultdict(list)
        for preds,feats in zip(predDictList,featDictList):
            if kk in feats:
                for pkey,pval in preds.items():
                    predDict[pkey].append(pval)
        for pkey,pvals in predDict.items():
            predDict[pkey]=np.array(pvals)



        for feats in featDictList2:
            del feats[kk]
        #print(featDictList2[0])
        featMat,dVec=vecFeats(featDictList2)
        print(avis)
        print(featMat.shape)
        print(predDict['lengde'].shape,predDict['churned'].shape,predDict['CPO'].shape)
        if ( (featMat[:,0].size/featMat[0,:].size)<3. ):
            print(avis,'has too few features',(featMat[:,0].size/featMat[0,:].size))
            continue
        print('---------------------------')


        avisDict[avis]=[featMat,predDict,dVec]
        featDictListTotal.extend(featDictList2)
        # if not predTotalCreated:
        #     predDictTotal=predDict
        #     predTotalCreated=True
        # else:
        #     for pkey,pvals in predDict.items():
        #         if len(pvals.shape)==1:
        #             predDictTotal[pkey]=np.concatenate([predDictTotal[pkey],pvals])
        #         else:
        #             predDictTotal[pkey]=np.vstack([predDictTotal[pkey],pvals])

    # featMat,dVec=vecFeats(featDictListTotal)
    # avisDict['TOTAL']=[featMat,predDictTotal,dVec]
    return avisDict


def vecFeats(featDList):
    dVec = DictVectorizer(sparse=False)
    mm=dVec.fit_transform(featDList)
    mm2=Imputer(missing_values='NaN', strategy='median', axis=0).fit_transform(mm)
    bigInds=np.unique(np.where(mm2>1.1)[1])
    for ind in bigInds:
        mm2[:,ind]=mm2[:,ind]/mm2[:,ind].max()
    return mm2,dVec

def getImportantCoeffs(clf,dVec,fun=lambda x:x.coef_[0],topN=10):
    fnames=dVec.get_feature_names()
    featList=fun(clf)
    absCoeffs=np.abs(featList)
    sortedInds=np.argsort(absCoeffs)[::-1][:topN]
    relImp=featList/absCoeffs.max()
    topFeats=[]
    for si in sortedInds:
        if np.abs(relImp[si])>0.2:
            topFeats.append((fnames[si],relImp[si]))
    return topFeats

def trainAvis(avis,avisDict,topCoeffsAvis,classifier,clfParams,toPred,baseInd=2):

    val=avisDict[avis]
    print('Avis:',avis)
    featMat=val[0]
    prints=[(key,v.shape) for key,v in val[1].items()]

    featVectorizer=val[2]

    predVals=val[1][toPred]
    if toPred=='CPO':
        predVals=predVals[:,baseInd]

    print(toPred,predVals.shape,prints)
    #input()

    # skf = StratifiedKFold(predVals, n_folds=4)
    # for train_index,test_index in skf:
    #     clf=classifier(**clfParams)
    #     X_train, X_test = featMat[train_index], featMat[test_index]
    #     y_train, y_test = predVals[train_index], predVals[test_index]
    #     clf.fit(X_train,y_train)
    #     y_pred=clf.predict(X_test)
    #     print(classification_report(y_test,y_pred))

    clf=classifier(**clfParams)
    X_train, X_test, y_train, y_test = train_test_split(featMat, predVals, test_size=.2)
    clf.fit(X_train,y_train)
    y_pred=clf.predict(X_test)
    y_score=clf.decision_function(X_test)
    topCoeffsAvis[avis]=getImportantCoeffs(clf,featVectorizer)
    classifierProperties={'classifier':clf,'y_score':y_score,'y_pred':y_pred,'y_true':y_test,\
        'roc_curve':metrics.roc_curve(y_test,y_score),'prec_recall':metrics.precision_recall_curve(y_test,y_score)}
    avisDict[avis].append(classifierProperties)
    print(classification_report(y_test,y_pred))
    print(topCoeffsAvis[avis])
    print('-------------------------------')
    print()


if __name__ == "__main__":
    print(9.4,225,234,1,800,8*225,8*234)
    sub_has_value(9.4,225,234,1,800)
