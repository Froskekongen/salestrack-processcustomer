
import sqlalchemy as sa

DBS={'AMEDIA':'32.10.190.102:1521/AMEDIA',\
    'ISDB':'32.10.190.100:1521/ISDB',\
    'ISRAPP':'32.10.190.100:1521/ISBUD',\
    'ISBUD':'32.10.190.102:1521/ISBUD'}





if __name__ == "__main__":
    import sys

    ##### NEVER USE CREATE OR DROP ON IS #####
    ##### ALL OBJECTS WITH _is HAS POTENTIAL FOR FUCKUP ####

    creds=sys.argv[1]
    DB=DBS[sys.argv[2]]

    engine_txt='oracle://'+creds+'@'+DB

    engine_is = sa.create_engine(engine_txt)
    ## Testin connection
    connection_is = engine_is.connect()
    result = connection_is.execute("select CUSTOMER_ID from customer")

    for iii,row in enumerate(result):
        print(row['customer_id'])
        if iii>10:
            break
    connection_is.close()

    meta_is=sa.MetaData(bind=engine_is,schema='INFOSOFT')

    customers_is = sa.Table('CUSTOMER', meta_is, autoload=True)

    ## test connection
    #print(meta.tables.keys())
    print(customers_is.columns)
    print()
    sel = sa.select([customers_is]).where(customers_is.c['customer_id']==3010065)
    print(sel)
    rr = sel.execute()
    for ilne in rr:
        print(ilne)
