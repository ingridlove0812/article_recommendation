# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 16:12:40 2020

@author: lailai_tvbs
"""
import time
import pandas as pd
import jieba_fast as jieba
from Tag_NewContent import set_path,get_data,getHtml,tmp_read,content_clean,tfidf_generate,get_similarity_values_tfidf_post
from itertools import chain


def return_post(text):
    tStart = time.time()
    set_path()
#    db_name = ['tvbs_v4', 'tvbs_news_v4', 'WarehouseServer', 'MartSe rver', 'TVBS_Test']
    content_all = pd.read_json(getHtml('http://34.80.91.60:5050/health/content_dev?day=90'))
#    content_update = pd.read_json(getHtml('http://34.80.91.60:8040/content?day=180'))
#    filt_push = pd.read_json(getHtml('http://34.80.91.60:8090/news_categoreis_filter'))/
    content_all.index = pd.Index(range(len(content_all)))
#    content_update.index = pd.Index(range(len(content_update)))
    tags = pd.read_json(getHtml('http://34.80.91.60:5050/health/tags'))
    tag_list = list(set(list(chain.from_iterable(content_all['tag'].apply(lambda x : x.split(',')).tolist()))))
#    dict_list = list(set(list(chain.from_iterable(tmp_read('dict_Health')['search_content'].apply(lambda x : x.split(' ')).tolist()))))
    dict_all = tag_list + list(tags['tag'])
    jieba.set_dictionary('dict.txt.big.txt')
    jieba.load_userdict(dict_all)
    content_clean(pd.read_json(getHtml('http://34.80.91.60:5050/health/content_dev?day=1')),'Health','MartServer_dev')
#    list_earth = list(set(filt_push[filt_push['news_category_id']==269]['news_id'].astype(str)))
    new_content_all = get_data('new_content', filt = '\',\''.join(content_all['article_id'].astype(str)), domain = 'Health')
    dictionary,tfidf,corr = tfidf_generate(new_content_all['new_content'])
    return get_similarity_values_tfidf_post(dictionary,tfidf,corr,text,new_content_all)
    tEnd = time.time()
    print ("all  -->  runtime : " + str(round((tEnd - tStart)/60,2)) + ' min')
