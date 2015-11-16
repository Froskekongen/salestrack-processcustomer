#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
