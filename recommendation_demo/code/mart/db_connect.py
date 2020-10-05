#DB Connection Tools

import pymongo
import mysql.connector

def connect_sql():
    conn = mysql.connector.connect(
            user='crm360',
            password='crm360_as!Wsd',
            host='crm360-db.cljcsr7rrceb.ap-southeast-2.rds.amazonaws.com',
            port=3306,
            charset='utf8mb4',
            database='tvbs_360')
    cur = conn.cursor()
    return conn, cur

def connect_sql_crm():
    conn = mysql.connector.connect(
            user='tvbs',
            password='tvbs_qzDw2Ae34',
            host='tvbs-0612.cljcsr7rrceb.ap-southeast-2.rds.amazonaws.com',
            port=3306,
            database='tvbs')
    cur = conn.cursor()
    return conn, cur

def connect_mongo():
    host = ['cluster0-shard-00-00-bnmv8.mongodb.net:27017',
            'cluster0-shard-00-01-bnmv8.mongodb.net:27017',
            'cluster0-shard-00-02-bnmv8.mongodb.net:27017']
    user = 'tvbs360'
    passwd = 'Tvbs360Pssw0rd'
    client = pymongo.MongoClient(host,
                          username=user,
						 password=passwd,
						 authMechanism='SCRAM-SHA-1',
                         replicaset='Cluster0-shard-0',
                         ssl=True)
    return client

def connect_mongo_dev():
    host = ['cluster360-dev-shard-00-00-bnmv8.mongodb.net:27017',
            'cluster360-dev-shard-00-01-bnmv8.mongodb.net:27017',
            'cluster360-dev-shard-00-02-bnmv8.mongodb.net:27017']
    user = 'tvbs360'
    passwd = 'Tvbs360Pssw0rd'
    client = pymongo.MongoClient(host,
                          username=user,
						 password=passwd,
						 authMechanism='SCRAM-SHA-1',
                         ssl=True)
    return client

def connect_sql_aws(database = 'tvbs_v4'):
    conn = mysql.connector.connect(
            user='tvbs',
            password='tvbstvbs',
            host='db41-ro-tvbs-aurora.clwuef820xta.ap-northeast-1.rds.amazonaws.com',
            port=3306,
            charset='utf8mb4',
            database = database)
    cur = conn.cursor()
    return conn, cur

def connect_sql_gcp(database = 'WarehouseServer'):
    conn = mysql.connector.connect(
            user='lailai',
            password='dsTVBS84305300tvbs',
            host='10.33.0.3',
            port=3306,
            database = database ,
            charset='utf8mb4'
            )
    cur = conn.cursor()
    return conn, cur