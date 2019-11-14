import os
import mysql.connector
import array
import json
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from django.conf import settings
import configparser,os

config = configparser.ConfigParser()

config.read(settings.CONFIGURATION)


from django.conf import settings
print=settings.LOGGER.info # once in each module
print("Logging is configured in DBUtils.")






MARIA_HOST=config.get('database','MARIA_HOST')
MARIA_PORT=config.get('database','MARIA_PORT')
MARIA_USER=config.get('database','MARIA_USER')
MARIA_PASSWORD=config.get('database','MARIA_PASSWORD')
MARIA_DB_IICB=config.get('database','MARIA_DB_IICB')
MARIA_DB_SCHEMA_SRES=config.get('database','MARIA_DB_SCHEMA_SRES')
MARIA_DB_SCHEMA_DOTS=config.get('database','MARIA_DB_SCHEMA_DOTS')
MARIA_DB_SCHEMA_CORE=config.get('database','MARIA_DB_SCHEMA_CORE')


# MARIA_HOST="localhost"
# MARIA_PORT="3306"
# MARIA_USER="root"
# MARIA_PASSWORD="root123"
# MARIA_DB_IICB="IICB_EUMICROBEDB"
# MARIA_DB_SCHEMA_SRES = "oomycetes_cgl_sres"
# MARIA_DB_SCHEMA_DOTS = "oomycetes_cgl_dots"
# MARIA_DB_SCHEMA_CORE = "oomycetes_cgl_core"

DBNAME = {'IICB':MARIA_DB_IICB,
       'SRES':MARIA_DB_SCHEMA_SRES,
       'DOTS':MARIA_DB_SCHEMA_DOTS,
       'CORE':MARIA_DB_SCHEMA_CORE
       }

def MariaConnection(dbname):
    MARIA_HOST_IP = os.getenv("MARIA_HOST", MARIA_HOST)
    MARIA_HOST_PORT = os.getenv("MARIA_PORT", MARIA_PORT)
    #print(MARIA_HOST_IP, MARIA_HOST_PORT)
    return mysql.connector.connect(user=MARIA_USER,password=MARIA_PASSWORD,host=MARIA_HOST_IP, \
                                   database=DBNAME[dbname],port=MARIA_HOST_PORT)

def MariaClose(db):
    db.close()

def MariaGetData(db, sqlquery):
    #print ("DB: ", db)
    cursor = db.cursor()
    #print ("CURSOR: ", cursor)

    cursor.execute(sqlquery)
    results = cursor.fetchall()
    #print ("RESULT: ", results)
    cursor.close()

    return results

def MariaSetData(db, sqlquery, datatuple):
    # print ("DB: ", db)
    cursor = db.cursor()
    # print ("CURSOR: ", cursor)

    results = cursor.execute(sqlquery, datatuple)
    db.commit()
    # print ("RESULT: ", results)
    cursor.close()