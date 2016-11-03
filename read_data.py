import json
#from pyLD import jsonld
import numpy as np


def load_data():
    articles = []
    ctg_set = set()
    this_articles, this_set = get_data('DM_Partial_0.jsonld')
    articles.append(this_articles)
    ctg_set = ctg_set.union(this_set)
    this_articles, this_set = get_data('DM_Partial_1.jsonld')
    articles.append(this_articles)
    ctg_set = ctg_set.union(this_set)
    this_articles, this_set = get_data('DM_Partial_2.jsonld')
    articles.append(this_articles)
    ctg_set = ctg_set.union(this_set)
    this_articles, this_set = get_data('DM_Partial_3.jsonld')
    articles.append(this_articles)
    ctg_set = ctg_set.union(this_set)
    this_articles, this_set = get_data('DM_Partial_4.jsonld')
    articles.append(this_articles)
    ctg_set = ctg_set.union(this_set)
    this_articles, this_set = get_data('DM_Partial_5.jsonld')
    articles.append(this_articles)
    ctg_set = ctg_set.union(this_set)
    this_articles, this_set = get_data('DM_Partial_6.jsonld')
    articles.append(this_articles)
    ctg_set = ctg_set.union(this_set)
    this_articles, this_set = get_data('DM_Partial_7.jsonld')
    articles.append(this_articles)
    ctg_set = ctg_set.union(this_set)
    this_articles, this_set = get_data('DM_Partial_8.jsonld')
    articles.append(this_articles)
    ctg_set = ctg_set.union(this_set)
    this_articles, this_set = get_data('DM_Partial_9.jsonld')
    articles.append(this_articles)
    ctg_set = ctg_set.union(this_set)
    this_articles, this_set = get_data('DM_Partial_10.jsonld')
    articles.append(this_articles)
    ctg_set = ctg_set.union(this_set)
    articles = np.reshape(np.array(articles), (1,0))
    return articles, ctg_set


def get_data(dir):

    with open('../IONData2016/dataset/DM_CleanData/' + dir) as json_data:
        data = json.load(json_data)

    content = data['@reverse']
    articles = []
    ctg_set = set()

    for i in range(0,len(content['publisher'])):
        this_id = content['publisher'][i]['@id']
        try:
            id_annotations = content['publisher'][i]['category']
        except Exception as e:
            #articles.append([this_id])
            continue
        articles.append([this_id, id_annotations])

        for annot in id_annotations:
            ctg_set.add(annot)

        #ctg_set = sorted(ctg_set)

    return articles, ctg_set


articles, ctg_set = load_data()
ctg_set = sorted(ctg_set)

ctg_to_id = {ctg_set[i]: i for i in range(0,len(ctg_set))}
id_to_ctg = {i:ctg_set[i] for i in range(0,len(ctg_set))}

print len(articles)
print articles[0][0]
article_vecs = []
for article in articles:
    article_vec = len(ctg_set)*[0]
    for ctg in article[1][1]:
        if ctg_to_id[ctg] is not None:
            #print ctg_to_id[ctg]
            article_vec[ctg_to_id[ctg]] = 1
    article_vecs.append([article[0],article_vec])
    #print article[0]
    #print article[1]
    break

# print article_vecs