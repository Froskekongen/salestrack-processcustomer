


def readConvert(fn):
    title_cn_to_key={}
    key_to_title_cn={}
    with open(fn) as ff:
        firstline=ff.readline()
        for line in ff:
            ll=line.split(',')
            ll=[l.strip() for l in ll]
            ll=[l.strip('"') for l in ll]
            key=ll[-1].strip()
            try:
                title_cn=(ll[1],int(ll[2]))
            except:
                print(ll)


            act=int(ll[3])
            if title_cn not in title_cn_to_key:
                title_cn_to_key[title_cn]=[]
            title_cn_to_key[title_cn].append((key,act))
            key_to_title_cn[key]=title_cn+(act,)
    return title_cn_to_key,key_to_title_cn
