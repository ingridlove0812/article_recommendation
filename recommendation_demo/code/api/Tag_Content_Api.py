# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 15:04:52 2020

@author: bruceyu1113
"""
import pymysql
#from db_config import mysql
from flask import jsonify,request,Flask
from flask_caching import Cache
from random import randint
import pandas as pd
import jieba_fast as jieba
import os
import sys
path = "C:/Users/Public/version_control/code/mart"
sys.path.insert(0, path)
from Tag_NewContent import get_data,getHtml,dict_generate,content_clean,weight_generate,get_similarity_values
os.chdir(path.replace('code','query')+'\\Tag_NewContent')


def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config["JSON_AS_ASCII"] = False
    app.config['CACHE_TYPE']='simple'
    cache = Cache()
    cache.init_app(app)
    # register the cache instance and binds it on to your app
    @app.route('/')
    @cache.cached(timeout=5)
    def home():
        return f'<h1>News Recommend API</h1>'


    @app.route('/news_content', methods=['GET'])
    def news_content():
#        now = datetime.now()
#        now_time = now.time()
        table = cache.get('news_content')
        if not table:
            content = get_data('content')
            table = content.to_json(force_ascii=False)
            cache.set('news_content',table,timeout=86100)
            return table
        else:
            return table


    @app.route('/news_jieba', methods=['GET'])
    def news_jieba():
#        now = datetime.now()
#        now_time = now.time()
        table = cache.get('news_jieba_content')
        if not table:
            data = pd.read_json(getHtml('http://34.80.91.60:8020/news_content'))
            tags = get_data('tags')
            dict_generate(tags)
            jieba.set_dictionary('dict.txt.big.txt')
            jieba.load_userdict('dict.txt')
            new_content = content_clean(data)
            table = new_content.to_json(force_ascii=False)
            cache.set('news_jieba_content',table,timeout=86200)
            return table
        else:
            return table


    @app.route('/news_lw', methods=['GET'])
    def news_lw():
#        now = datetime.now()
#        now_time = now.time()
        table = cache.get('news_local_weight')
        if not table:
            content = pd.read_json(getHtml('http://34.80.91.60:8020/news_content'))
            jieba = pd.read_json(getHtml('http://34.80.91.60:8020/news_jieba'), typ='series')
            lw = weight_generate(content,jieba)
            table = lw.to_json(force_ascii=False)
            cache.set('news_local_weight',table,timeout=86200)
            return table
        else:
            return table


    @app.route('/news_result', methods=['GET'])
    def news_result():
#        now = datetime.now()
#        now_time = now.time()
        table = cache.get('news_result')
        if not table:
            content = pd.read_json(getHtml('http://34.80.91.60:8020/news_content'))
            lw = pd.read_json(getHtml('http://34.80.91.60:8020/news_lw'), typ='series')
            result = get_similarity_values('1370539')
            table = result.to_json(force_ascii=False)
            cache.set('news_result',table,timeout=86400)
            return table
        else:
            return table

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8020,debug=True, use_reloader=False)
