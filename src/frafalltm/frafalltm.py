

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

def parse_row(rr,heads):
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

    dateInds=[0,1,12]
    for ind in dateInds:
        rr[ind]=parseDate(rr[ind])

    ## Customer churn and (current) length of subscription
    if rr[1]=='Aktiv':
        predDict['aktiv']=0
        predDict['lengde']=5000 #impute. Not good imputing. For
    else:
        predDict['aktiv']=1
        predDict['lengde']=(row[1]-row[0]).days

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

def make_avis_dict(aviser,featDictList,churned,abo_lengde):
    avisDict={}
    for avis in aviser:
        kk='Avis_'+avis
        featDictList2=[feats for feats in featDictList if avis in feats]
        churned2=[ch for ch,feats in zip(churned,featDictList) if avis in feats]
        churned2=np.array(churned2)
        abo_lengde2=[ch for ch,feats in zip(abo_lengde,featDictList) if avis in feats]
        abo_lengde2=np.array(abo_lengde2)
        for feats in featDictList2:
            del feats[avis]
        avisDict[avis]=[featDictList2,churned2,abo_lengde2]
    return avisDict

dVec = DictVectorizer(sparse=False)
def vecFeats(featDList):
    mm=dVec.fit_transform(featDList)
    mm2=Imputer(missing_values='NaN', strategy='median', axis=0).fit_transform(mm)
    bigInds=np.unique(np.where(mm2>1.1)[1])
    for ind in bigInds:
        mm2[:,ind]=mm2[:,ind]/mm2[:,ind].max()
    return mm2



if __name__ == "__main__":
    with open('/mnt/tmsales/qlik_tmsales.csv') as ff:
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
                featDict,predDict=parse_row(row,heads)
                featDictList.append(featDict)
                churned.append(predDict['aktiv'])
                abo_lengde.append(predDict['lengde'])
                aviser.add(row[6])

    churned=np.array(churned)
    abo_lengde=np.array(abo_lengde)

    avisDict=make_avis_dict(aviser,featDictList,churned,abo_lengde)
    skf = StratifiedKFold(churned2, n_folds=4)
    logRegParams={n_jobs:-1,class_weight:'balanced',penalty:'l1',C:0.5}

    for avis in avisDict:
        featMat=vecFeats(avis[0])
        churned=avis[1]
        logReg=LogisticRegression(**logRegParams)
        skf = StratifiedKFold(churned, n_folds=4)
        print(avis)
        for train_index,test_index in skf:
                X_train, X_test = featMat[train_index], featMat[test_index]
                y_train, y_test = churned[train_index], churned[test_index]
                logReg.fit(X_train,y_train)
                y_pred=logReg.predict(X_test)
                print(classification_report(y_test,y_pred))

        logReg=LogisticRegression(**logRegParams)
        X_train, X_test, y_train, y_test = train_test_split(featMat, churned, test_size=.2)
        y_pred=logReg.predict(X_test)
        y_score=logReg.decision_function(X_test)
        print(classification_report(y_test,y_pred))
        print(avis)
        print('-------------------------------')
        print()
