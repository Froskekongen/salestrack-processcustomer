


def line_proc(filename,title_cn_to_key):
    """
    We want all users with traffic to be connected to an INFOSOFT customer, if possible.
    """
    intInds=[0,3,4,8,9,10,12,13,18,19,36,38]
    floatInds=[11,15]
    keepInds=[2,6,8,9,10,11,13,22,25,26,33,34,36,37,38,39,40,43]
    N_keep_cols=len(keepInds)



    customerDictList=[]

    N_not_key=0
    N_rec=0
    with open(filename) as ff:
        firstline=ff.readline().split('\t')
        firstline[-1]=firstline[-1].strip()
        N_cols=len(firstline)

        keepCols=[firstline[ind] for ind in keepInds]
        keepCols.append('isactive')


        for line in ff:
            N_rec+=1
            vals=line.replace(',','.')
            vals=line.replace('%','')
            vals=line.split('\t')
            vals = [val.strip() for val in vals]
            key=(vals[2],int(vals[0]))
            try:
                ukeys=title_cn_to_key[key]
                #print(key,ukeys)
            except:
                N_not_key+=1
                if N_not_key%100==0:
                    print(key,N_not_key,N_rec,N_not_key/N_rec)
                continue


            for ind in intInds:
                try:
                    vals[ind]=int(vals[inds])
                except Exception as _:
                    pass
            for ind in floatInds:
                try:
                    vals[ind]=float(vals[ind])
                except Exception as _:
                    vals[ind]=float('nan')

            retVals=[vals[ind] for ind in keepInds]

            for ukey in ukeys:
                print(key,ukey)
                customerDictList.append({ukey[0]:retVals+[ukey[1]]})
    return customerDictList,firstline




def mergeCustomers(cd1,cd2):
    pass


if __name__ == "__main__":
    import a_key_konversion
    import sys
    cdFN=sys.argv[1]
    title_cn_to_key,key_to_title_cn=a_key_konversion.readConvert(cdFN)
    exFile='/home/erlenda/salestrack/Customer_Daily/Daily_CustomerFile_20151012.txt'

    cDictList=line_proc(exFile,title_cn_to_key)
