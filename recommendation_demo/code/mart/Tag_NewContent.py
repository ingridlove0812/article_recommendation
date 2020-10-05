# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 16:12:40 2020

@author: lailai_tvbs
"""

import os
import pandas as pd
import numpy as np
from db_connect import connect_sql_gcp, connect_sql_aws
from w3lib.html import remove_tags, replace_entities
#from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import jieba_fast as jieba
from collections import defaultdict
from gensim import corpora,models#,similarities
import re
from sklearn.metrics.pairwise import cosine_similarity as cs
import urllib.request

def set_path():
    if len(__file__) <= 50:
        path = os.getcwd().replace('code','query')+'\\'+__file__.replace('.py','')
    else:
        path = __file__.replace('code','query').replace('.py','')
    os.chdir(path)

def getHtml(url):
    hds = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'}
    page1 = urllib.request.Request(url, headers = hds)
    page = urllib.request.urlopen(page1)
    html=page.read()
    return html


#從txt匯入query
def get_query(query_name,date_name = 'null', filt_name = 'null', filt_name1 = 'null'):
    query = ''
    with open(query_name + ".txt", "r") as file:
        if date_name != 'null' or filt_name != 'null':
            query = file.read().format(date = date_name, filt = filt_name, filt1 = filt_name1)
        else:
            query = file.read()
        file.close()
    return query


#從GCP主機拉資料
def pull_data_gcp(db_name, select, string = 'null', integer = 'null'):
    conn, cur = connect_sql_gcp(db_name)
    cur.execute(select)
    cols = [i[0] for i in cur.description]
    tmp_data = cur.fetchall()
    tmp_data = pd.DataFrame(tmp_data, columns = cols)
    if string != 'null':
        tmp_data[string] = tmp_data[string].select_dtypes([np.object]).stack().str.decode('utf-8').unstack()
    if integer != 'null':
        for l in integer:
            tmp_data[l] = tmp_data[l].fillna(0).replace('',0).astype(int)
    cur.close()
    conn.close()
    return tmp_data


#從AWS主機拉資料
def pull_data_aws(db_name, select, string = 'null', integer = 'null'):
    conn, cur = connect_sql_aws(db_name)
    cur.execute(select)
    cols = [i[0] for i in cur.description]
    tmp_data = cur.fetchall()
    tmp_data = pd.DataFrame(tmp_data, columns = cols)
    #將文字轉成utf8碼
    if string != 'null':
        tmp_data[string] = tmp_data[string].select_dtypes([np.object]).stack().str.decode('utf-8').unstack()
    #將有些應該是數字的欄位修改成int
    if integer != 'null':
        for l in integer:
            tmp_data[l] = tmp_data[l].fillna(0).replace('',0).astype(int)
    cur.close()
    conn.close()
    return tmp_data

def dict_generate(tags):
    txt = ''
    for t in tags['tag'].apply(lambda x : np.char.upper(x)):
        txt += t + '\n'
    path = 'C:\\Users\\lailai_tvbs\\D\\python\\query\\Mart\\Tag_NewContent\\'
    f = open(path + 'dict.txt', 'w', encoding = 'utf-8')
    f.write(txt)


def content_clean(content):
    #去除html標記和encode標點符號
    clean_content = content['news_content'].apply(lambda x : remove_tags(replace_entities(x)))
    #將所有英文轉小寫
    clean_content = clean_content.apply(lambda x : np.char.upper(x))
    #匯入停用詞名單
    stopwords = open("stopwords.txt").read().split()
    #用結巴斷詞
    jieba_content = clean_content.apply(lambda x : [w for w in jieba.cut(x) if len(w) > 1 and re.compile(r"[A-Z\u4e00-\u9fa5]").findall(w)])
    jieba_remove = jieba_content.apply(lambda x : [w for w in x if w not in stopwords])
    #將剩下詞組依文章貼回去
    new_content= jieba_remove.apply(lambda x : ' '.join(x))
    return new_content


def tfidf_generate(content,new_content):
    #把所有慈整理起來
    documents = list(new_content)
    #把詞切成list
    texts = [[word for word in document.split()] for document in documents]
    #計算總詞頻
    frequency = defaultdict(int)
    for text in texts:
        for word in text:
            frequency[word]+=1
    #將總辭頻低於10的詞拿掉
    texts = [[word for word in text if frequency[word] > 10] for text in texts]
    #建立文本的總詞庫
    dictionary = corpora.Dictionary(texts)
    #將詞庫轉矩陣
    corpus = [dictionary.doc2bow(text) for text in texts]
    #將新的詞庫矩陣算出tfidf
    tfidf = models.TfidfModel(corpus)
    #找出詞庫個數
#    featurenum = len(dictionary.token2id.keys())
    #利用詞庫矩陣建立相關索引
#    index = similarities.SparseMatrixSimilarity(tfidf[corpus],num_features=featurenum)
    return dictionary,tfidf



def weight_generate(content,new_content):
    #把所有慈整理起來
    documents = list(new_content)
    #把詞切成list
    texts = [[word for word in document.split()] for document in documents]
    #計算總詞頻
    frequency = defaultdict(int)
    for text in texts:
        for word in text:
            frequency[word]+=1
    #將總辭頻低於10的詞拿掉
    texts = [[word for word in text if frequency[word] >= 5] for text in texts]
    #建立文本的總詞庫
    dictionary = corpora.Dictionary(texts)
    ind = pd.DataFrame(list(dictionary.items()),columns = ['index','word'])

    #計算文章詞頻
    ind_list = list(ind['word'])
    metrix = pd.DataFrame(ind['word'])
    for i in range(len(new_content)):#len(new_content)
        wordcnt = {word : 0 for word in ind['word']}
        for word in new_content[i].split():
            if word in ind_list:
                wordcnt[word]+=1
        wordcnt_tmp = pd.DataFrame(list(wordcnt.items()),columns = ['word','cnt'])
        exec("metrix['%s'] = wordcnt_tmp['cnt']" %(content['news_id'][i]))
    metrix = metrix.reset_index()
    metrix['index'] = metrix['index'].astype(str)
#    index = metrix[['index','word']]
#    metrix_tmp = metrix.drop(['index','word'], axis=1)
    metrix_cnt = metrix.drop(['index','word'], axis=1)
#    metrix_tmp = metrix_tmp.div(metrix_tmp.sum(axis=1), axis=0)
#    metrix_tmp = metrix_tmp*np.log(metrix_tmp)
#    gw = metrix_tmp.sum(axis=1)/np.log(len(content['news_id']))+1
    lw = np.log(metrix_cnt+1)
    return lw


def get_similarity_values(article_id):
    global content,lw
    sim = cs(lw.T.as_matrix(), lw[[article_id]].T.as_matrix())
    result_tmp = pd.DataFrame(sim).sort_values(by = 0, ascending = False)[1:11]
    result = content[content.index.isin(list(result_tmp.index))]['news_title']
    return result

def content_tag(i):
    global jieba, dictionary, tfidf
    row_content = jieba[0]
    #文本轉成矩陣
    new_xs = dictionary.doc2bow(row_content)
    #找出相關性>0.2的詞並新增回去
    sim = pd.DataFrame(tfidf[new_xs])
    content.loc[i,'new_tag'] = ','.join([dictionary[ind] for ind in sim[sim[1]>0.1].sort_values(by = 1, ascending = False)[0]])

def get_data(typ):
    db_name = ['tvbs_v4', 'tvbs_news_v4', 'WarehouseServer', 'MartSe rver', 'TVBS_Test']
    tags = pull_data_gcp(db_name[2], get_query('API_NewsTag'))
    content = pull_data_aws(db_name[1], get_query('News_content'))
    if typ == 'tags':
        return tags
    elif typ == 'content':
        return content
