# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 16:12:40 2020

@author: lailai_tvbs
"""
import time
import pandas as pd
import jieba_fast as jieba
from Tag_NewContent import set_path,get_data,getHtml,tmp_read,content_clean,tfidf_generate,get_similarity_values_tfidf
from itertools import chain


if __name__ == '__main__':
    tStart = time.time()
    getHtml('http://34.80.91.60:5050/health/recommend_list_dev')
    set_path()
#    db_name = ['tvbs_v4', 'tvbs_news_v4', 'WarehouseServer', 'MartServer', 'TVBS_Test']
    content_all = pd.read_json(getHtml('http://34.80.91.60:5050/health/content_dev?day=1080'))
    content_update = pd.read_json(getHtml('http://34.80.91.60:5050/health/content_update_dev'))
#    filt_push = pd.read_json(getHtml('http://34.80.91.60:8090/news_categoreis_filter'))/
    content_all.index = pd.Index(range(len(content_all)))
    content_update.index = pd.Index(range(len(content_update)))
    tags = pd.read_json(getHtml('http://34.80.91.60:5050/health/tags'))
    tag_list = list(set(list(chain.from_iterable(content_all['tag'].apply(lambda x : x.split(',')).tolist()))))
#    domain_lst = ['News', 'Woman', 'Supertaste','Health','Product']
    tmp = pd.read_json(getHtml('http://34.80.91.60:5050/health/gsc'))
#    gsc = pd.read_json(getHtml('http://34.80.91.60:5050/health/gsc'))
#    dict_list = []
#    for domain in domain_lst:
#        tmp_list = list(set(list(chain.from_iterable(tmp_read('dict_' + domain)['search_content'].apply(lambda x : x.split(' ')).tolist()))))
#        dict_list.extend(tmp_list)
    dict_list = list(set(list(chain.from_iterable(tmp['query'].apply(lambda x : x.split(' ')).tolist()))))
    dict_all = tag_list + dict_list + list(tags['tag'])
    jieba.set_dictionary('dict.txt.big.txt')
    jieba.load_userdict(dict_all)
    content_clean(pd.read_json(getHtml('http://34.80.91.60:5050/health/content_dev?day=7')),'Health', 'MartServer_dev')
#    list_earth = list(set(filt_push[filt_push['news_category_id']==269]['news_id'].astype(str)))
    new_content_all = get_data('new_content_dev', filt = '\',\''.join(content_all['article_id'].astype(str)), domain = 'Health')
    new_content = get_data('new_content_dev', filt = '\',\''.join(content_update['article_id'].astype(str)), domain = 'Health')
    dictionary,tfidf,corr = tfidf_generate(new_content_all['new_content'])
    get_similarity_values_tfidf(dictionary,tfidf,corr,new_content,new_content_all,'Health', 'MartServer_dev')
    tEnd = time.time()
    print ("all  -->  runtime : " + str(round((tEnd - tStart)/60,2)) + ' min')
