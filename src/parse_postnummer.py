#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
from datetime import datetime
from collections import defaultdict

class ParsePostnummer(object):
    def __init__(self,infile='../data/Postnummerregister_utf8.txt'):
        """
        Format: postnummer\tpoststed\tkommunekode\tkommunenavn\tkategori
        """
        self.infile=infile
        self.pnlist=self.parsefile()
        self.pn_to_navn=self._pn_to_navn()
        self.pn_to_kkode=self._pn_to_kkode()

    def parsefile(self):
        with open(self.infile) as ff:
            pnlist=[]
            for line in ff:
                ss=line.split('\t')
                ss=[s.strip() for s in ss]
                ss[0]=int(ss[0])
                ss[2]=int(ss[2])
                pnlist.append(ss)
        return pnlist

    def _pn_to_navn(self):
        return {s[0]:s[3] for s in self.pnlist}

    def _pn_to_kkode(self):
        return {s[0]:s[2] for s in self.pnlist}

class ParseAvisKategori(object):
    def __init__(self,infile='../data/avis_kategori.csv'):
        """
        Format: postnummer\tpoststed\tkommunekode\tkommunenavn\tkategori
        """
        self.infile=infile
        self.avis=self.parsefile()
        #print(self.aviser)


    def parsefile(self):
        with open(self.infile,newline='\n') as ff:
            self.aviser=[]
            self.avisDict={}
            self.veiklasser=defaultdict(set)
            csvread = csv.reader(ff, delimiter='\t')
            for iii,row in enumerate(csvread):
                row=[r.lower() for r in row]
                if iii==0:
                    self.heads=row
                    continue
                row[2]=int(row[2])

                if row[5]!='#n/a':
                    row[5]=datetime.strptime(row[5],'%m/%d/%Y')
                self.veiklasser[row[2]].add(row[1])
                self.aviser.append(row)
                self.avisDict[row[1]]=row

    def avisVeiklasse(self,avis):
        try:
            return self.avisDict[avis.lower()][2]
        except KeyError as e:
            return -1

    def veiKlasseAvis(self,veiklasse,avis):
        return avis.lower() in self.veiklasser[veiklasse]



if __name__ == "__main__":
    parseAvis=ParseAvisKategori()
