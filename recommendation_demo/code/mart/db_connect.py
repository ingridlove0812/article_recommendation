#DB Connection Tools

import pymongo
import mysql.connector

def connect_sql():
    conn = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            port=3306,
            charset='utf8mb4',
            database='tvbs_360')
    cur = conn.cursor()
    return conn, cur

def connect_sql_crm():
    conn = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            port=3306,
            database='tvbs')
    cur = conn.cursor()
    return conn, cur

def connect_mongo():
    host = host
    user = user
    passwd = password
    client = pymongo.MongoClient(host,
                          username=user,
						 password=passwd,
						 authMechanism='SCRAM-SHA-1',
                         replicaset='Cluster0-shard-0',
                         ssl=True)
    return client

def connect_mongo_dev():
    host = host
    user = user
    passwd = password
    client = pymongo.MongoClient(host,
                          username=user,
						 password=passwd,
						 authMechanism='SCRAM-SHA-1',
                         ssl=True)
    return client

def connect_sql_aws(database = 'tvbs_v4'):
    conn = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            port=3306,
            charset='utf8mb4',
            database = database)
    cur = conn.cursor()
    return conn, cur

def connect_sql_gcp(database = 'WarehouseServer'):
    conn = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            port=3306,
            database = database ,
            charset='utf8mb4'
            )
    cur = conn.cursor()
    return conn, cur
