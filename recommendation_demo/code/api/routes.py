# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 16:13:45 2021

@author: bruceyu1113
"""
import pymysql
import sys
import requests
import os
#import numpy as np
from flask import Blueprint,request,jsonify
from datetime import datetime
path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, path)
from cache import cache
from df_to_json import dataframe_to_json
import db_config
import update_News_Recommend_last1
import tag_recom_algorithm as tra
import articleRecomTag as tagrec



#from recom.cache import cache
#from recom import db_config
#from recom import update_News_Recommend_last1
#from recom import tag_recom_algorithm as tra
#from recom import news_articleRecomTag as newsTagRec
#

##宣告Blueprint route名稱##
news = Blueprint('news',__name__,url_prefix='/news')
##

mysql = db_config.mysql


@news.route('/getdata')
def getdata():
    return{'news': 'value'}
# =============================================================================
@news.route('test',methods = ['GET'])
def test_db():
    db_config.aws_db()
    insert = """SELECT news_id AS nid,
                news_get_type AS get_type,
                news_title AS title,
                news_tag AS tag,
                news_summary AS summary,
        	    cast(DATE(news_published_date)as char) AS date
           FROM tvbs_news_v4.news_v4
            WHERE DATE(news_published_date) >= SUBDATE(CURDATE(), INTERVAL 1 DAY)
        	AND DATE(news_published_date) <= CURDATE()
        	AND news_status = 1 AND news_get_type != 8 AND news_id not in (select news_id FROM tvbs_news_v4.news_v4_category_mapping where news_category_id=14);"""
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute(insert)
    rows = cur.fetchall()
    news_table=jsonify(rows)    
    cur.close()
    conn.close()
    return(news_table)
# =============================================================================   
#    
##後台文章API
@news.route('/article_cache', methods=['GET'])
#@cache.cached(timeout=300)
def aws_news_api():
    args = request.args
#            now = datetime.now()
    hour = datetime.now().hour
    minute = datetime.now().minute
    day = args.get('day') if 'day' in args else 90
    news_table = cache.get('news_cache_'+str(day))
    if day ==90:
        if not news_table or \
        ((hour>0 and minute > 0) and (hour>0 and minute <= 1)) or ((hour>6 and minute > 0) and (hour>6 and minute <= 1)) or \
        ((hour>8 and minute > 0) and (hour>8 and minute <= 1)) or ((hour>10 and minute > 0) and (hour>10 and minute <= 1)) or \
        ((hour>12 and minute > 0) and (hour>12 and minute <= 1)) or ((hour>14 and minute > 0) and (hour>14 and minute <= 1)) or \
        ((hour>16 and minute > 0) and (hour>16 and minute <= 1)) or ((hour>18 and minute > 0) and (hour>18 and minute <= 1)) or \
        ((hour>20 and minute > 0) and (hour>20 and minute <= 1)) or ((hour>22 and minute > 0) and (hour>22 and minute <= 1)):
#                if not news_table or(now_time >= time(00,0) and now_time <= time(00,2)) :
            db_config.aws_db()
            insert = """SELECT news_id AS nid,
                            news_get_type AS get_type,
                            news_title AS title,
                            news_tag AS tag,
                            news_summary AS summary,
                    	    cast(DATE(news_published_date)as char) AS date
                       FROM tvbs_news_v4.news_v4
                        WHERE DATE(news_published_date) >= SUBDATE(CURDATE(), INTERVAL 90 DAY)
                    	AND DATE(news_published_date) <= CURDATE()
                    	AND news_get_type != 8 AND news_status = 1 AND news_id not in (select news_id FROM tvbs_news_v4.news_v4_category_mapping where news_category_id=14);"""
            print('Not cache')
            conn = mysql.connect()
            cur = conn.cursor(pymysql.cursors.DictCursor)
            cur.execute(insert)
            rows = cur.fetchall()
            news_table=jsonify(rows)
            news_table.status_code=200
            cache.set('news_cache_'+str(day),news_table,timeout=7200)
            cur.close()
            conn.close()
            return news_table
        else:
            print('the day is 90 and news_cache')
            return news_table
    else:
        if not news_table:
            print('Not cache')
            db_config.aws_db()
            insert = """SELECT news_id AS nid,
                            news_get_type AS get_type,
                            news_title AS title,
                            news_tag AS tag,
                            news_summary AS summary,
                    	    cast(DATE(news_published_date)as char) AS date
                       FROM tvbs_news_v4.news_v4
                        WHERE DATE(news_published_date) >= SUBDATE(CURDATE(), INTERVAL %s DAY)
                    	AND DATE(news_published_date) <= CURDATE()
                    	AND news_get_type != 8 AND news_status = 1 AND news_id not in (select news_id FROM tvbs_news_v4.news_v4_category_mapping where news_category_id=14);""" % (day)
            conn = mysql.connect()
            cur = conn.cursor(pymysql.cursors.DictCursor)
            cur.execute(insert)
            rows = cur.fetchall()
            news_table=jsonify(rows)
            news_table.status_code=200
            cache.set('news_cache_'+str(day),news_table,timeout=3600)
            cur.close()
            conn.close()
            return news_table
        else:
            print('news_cache')
            return news_table

##News 標籤推薦API
@news.route('/tag_score_table', methods=['GET'])
#    @cache.cached(timeout=5)
def tvbs_news_tag_analysis():
    hour = datetime.now().hour
    minute = datetime.now().minute
    args = request.args
    day = args.get('day') if 'day' in args else 90
    news_tag_summary = cache.get('news_tag_cache'+str(day))
    try:
        if (not news_tag_summary) or\
            ((hour>0 and minute > 0) and (hour>0 and minute <= 1)) or ((hour>6 and minute > 0) and (hour>6 and minute <= 1)) or \
            ((hour>8 and minute > 0) and (hour>8 and minute <= 1)) or ((hour>10 and minute > 0) and (hour>10 and minute <= 1)) or \
            ((hour>12 and minute > 0) and (hour>12 and minute <= 1)) or ((hour>14 and minute > 0) and (hour>14 and minute <= 1)) or \
            ((hour>16 and minute > 0) and (hour>16 and minute <= 1)) or ((hour>18 and minute > 0) and (hour>18 and minute <= 1)) or \
            ((hour>20 and minute > 0) and (hour>20 and minute <= 1)) or ((hour>22 and minute > 0) and (hour>22 and minute <= 1)):
#            if (not news_tag_summary):
            print('Not cache')
            back_tag_of_dfItem = tra.cache_article_table('news').get_aws_table_cache(day)
            tag_summary = tra.editorTag('news',back_tag_of_dfItem,'N').editor_tag_summary()
            summary_list = dataframe_to_json(tag_summary)
            news_tag_summary = jsonify(summary_list)
            news_tag_summary.status_code=200
            cache.set('news_tag_cache'+str(day),news_tag_summary,timeout=7200)
            return news_tag_summary
        else:
            print('news_tag_cache')
            return news_tag_summary
    finally:
        print('request get /tvbs_news_tag_analysis')

##後台文章API
@news.route('/news-recom-batch-update', methods=['GET'])
#    @cache.cached(timeout=300)
def news_recom_batch_update():
#            args = request.args
#            batch = args.get('batch_date') if 'batch_date' in args else None
        batch = request.args.get('batch_date', 1, type = int)
#            batch = request.args['batch_date']
#            now = datetime.now()
        hour = datetime.now().hour
        minute = datetime.now().minute
        if batch ==0:
            news_update_table_all = cache.get('news_cache_'+str(batch))
            if not news_update_table_all:
                print('Not cache')
                db_config.gcp_db()
                insert = """SELECT nid,recom_nid FROM NMServer.News_Recommend;"""
                conn = mysql.connect()
                cur = conn.cursor(pymysql.cursors.DictCursor)
                cur.execute(insert)
                rows = cur.fetchall()
                news_update_table_all=jsonify(rows)
                news_update_table_all.status_code=200
                cache.set('news_cache_'+str(batch),news_update_table_all,timeout=7200)
                cur.close()
                conn.close()
                return news_update_table_all
            else:
                print('Cache news_batch')
                return news_update_table_all
        elif batch ==1:
            news_update_table = cache.get('news_cache_'+str(batch))
            if not news_update_table or \
            ((hour>1 and minute > 0) and (hour>1 and minute <= 1)) or ((hour>18 and minute > 0) and (hour>18 and minute <= 1)):
                print('Not cache')
                db_config.gcp_db()
                insert = """SELECT nid,recom_nid FROM NMServer.News_Recommend WHERE date(last_modified_date) = CURDATE();"""
                conn = mysql.connect()
                cur = conn.cursor(pymysql.cursors.DictCursor)
                cur.execute(insert)
                rows = cur.fetchall()
                news_update_table=jsonify(rows)
                news_update_table.status_code=200
                cache.set('news_cache_'+str(batch),news_update_table,timeout=7200)
                cur.close()
                conn.close()
                return news_update_table
            else:
                print('news_batch_cache_True')
                return news_update_table
        else:
            return jsonify({"error":"error information. please input batch_date 0 or 1"})
##News 推薦文章API
@news.route('/post_recommend',methods=['POST'])
def tvbs_news_recommend():
    result={}
    temp_json = request.get_json(force=True)
    new_record, new_record_recom_nid = update_News_Recommend_last1.update_News_Recommend_last1(temp_json['nid'],temp_json['get_type'],temp_json['title'],temp_json['tag'],temp_json['summary'],temp_json['date'])
#        for index, row in new_record_recom_nid.iterrows():
#            #result[index] = row.to_json()
#            result[index] = dict(row)
    result = new_record_recom_nid[['recom_nid']].to_dict('r')[0]
    return jsonify(result)

##News 推薦標籤API
@news.route('/post_tag_recommend',methods=['POST'])
def tvbs_news_tag_recommend():
    result={}
    temp_json  = request.get_json(force=True)
#    tag_recommentTop20 = newsTagRec.get_tag_recommend(temp_json['article'])
    tag_recommentTop20 = tagrec.get_tag_recommend('news',temp_json['article'],'N')
    result = {'recomment_tag':tag_recommentTop20}
    return jsonify(result)

@news.route('/deleted_endpoint',methods=['POST'])
def delete_endpoint():
    temp_json  = request.get_json(force=True)
    return jsonify(temp_json)

@news.route('/print_log',methods=['GET'])
def print_log():
    requests.get(f"http://34.80.91.60:5050/lineNotify/LineNotify-news-error?ip_address={request.remote_addr}&request_url={request.url}")
    addr = request.remote_addr
    url = request.url
    temp_json = {"addr" : addr,"url":url}
    return jsonify(temp_json)

##error message       
@news.app_errorhandler(404)
def not_found(e):
#    news.logger.error(f"not found:{e},route:{request.url}")
    error_message = e
    requests.get(f"http://34.80.91.60:5050/linenotify/error?ip_address={request.remote_addr}&message={error_message}&request_url={request.url}")
    message={
            'status':404,
            'message': 'not found ' + request.url
            }
    resp = jsonify(message)
#    resp.status_code = 404
    return resp

@news.app_errorhandler(500)
def server_error(e):
#    news.logger.error(f"Server error:{e},route:{request.url}")
    error_message = e
    requests.get(f"http://34.80.91.60:5050/linenotify/error?ip_address={request.remote_addr}&message={error_message}&request_url={request.url}")
    message={
            'status':500,
            'message': 'server error ' + request.url
            }
    resp = jsonify(message)
#    resp.status_code = 500
    return resp

@news.app_errorhandler(403)
def forbidden(e):
#    news.logger.error(f"Forbidden access:{e},route:{request.url}")
    error_message = e
    requests.get(f"http://34.80.91.60:5050/linenotify/error?ip_address={request.remote_addr}&message={error_message}&request_url={request.url}")
    message={
            'status':403,
            'message': 'server error ' + request.url
            }
    resp = jsonify(message)
#    resp.status_code = 403
    return resp
