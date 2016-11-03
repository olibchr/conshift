import json
#from pyLD import jsonld
import numpy as np
import csv


NO_ANT_CNT = 0
NO_CTG_CNT = 0
ERR_CNT = 0

def load_data():
    ctg_set = set()
    """
    DMa, this_set = get_data('DM_CleanData/DM_Partial_0.jsonld')
    ctg_set = ctg_set.union(this_set)
    DMb, this_set = get_data('DM_CleanData/DM_Partial_1.jsonld')
    ctg_set = ctg_set.union(this_set)
    DMc, this_set = get_data('DM_CleanData/DM_Partial_2.jsonld')
    ctg_set = ctg_set.union(this_set)
    DMd, this_set = get_data('DM_CleanData/DM_Partial_3.jsonld')
    ctg_set = ctg_set.union(this_set)
    DMe, this_set = get_data('DM_CleanData/DM_Partial_4.jsonld')
    ctg_set = ctg_set.union(this_set)
    DMf, this_set = get_data('DM_CleanData/DM_Partial_5.jsonld')
    ctg_set = ctg_set.union(this_set)
    DMg, this_set = get_data('DM_CleanData/DM_Partial_6.jsonld')
    ctg_set = ctg_set.union(this_set)
    DMh, this_set = get_data('DM_CleanData/DM_Partial_7.jsonld')
    ctg_set = ctg_set.union(this_set)
    DMi, this_set = get_data('DM_CleanData/DM_Partial_8.jsonld')
    ctg_set = ctg_set.union(this_set)
    DMj, this_set = get_data('DM_CleanData/DM_Partial_9.jsonld')
    ctg_set = ctg_set.union(this_set)
    DMk, this_set = get_data('DM_CleanData/DM_Partial_10.jsonld')
    ctg_set = ctg_set.union(this_set)

    HPa, this_set = get_data('HP_CleanData/HP_Partial_0.jsonld')
    ctg_set = ctg_set.union(this_set)
    HPb, this_set = get_data('HP_CleanData/HP_Partial_1.jsonld')
    ctg_set = ctg_set.union(this_set)
    HPc, this_set = get_data('HP_CleanData/HP_Partial_2.jsonld')
    ctg_set = ctg_set.union(this_set)
    HPd, this_set = get_data('HP_CleanData/HP_Partial_3.jsonld')
    ctg_set = ctg_set.union(this_set)
    HPe, this_set = get_data('HP_CleanData/HP_Partial_4.jsonld')
    ctg_set = ctg_set.union(this_set)
    HPf, this_set = get_data('HP_CleanData/HP_Partial_5.jsonld')
    ctg_set = ctg_set.union(this_set)
    HPg, this_set = get_data('HP_CleanData/HP_Partial_6.jsonld')
    ctg_set = ctg_set.union(this_set)
    HPh, this_set = get_data('HP_CleanData/HP_Partial_7.jsonld')
    ctg_set = ctg_set.union(this_set)
    HPi, this_set = get_data('HP_CleanData/HP_Partial_8.jsonld')
    ctg_set = ctg_set.union(this_set)
    HPj, this_set = get_data('HP_CleanData/HP_Partial_9.jsonld')
    ctg_set = ctg_set.union(this_set)

    INDa, this_set = get_data('IND_CleanData/IND_Partial_0.jsonld')
    ctg_set = ctg_set.union(this_set)
    INDb, this_set = get_data('IND_CleanData/IND_Partial_1.jsonld')
    ctg_set = ctg_set.union(this_set)
    INDc, this_set = get_data('IND_CleanData/IND_Partial_2.jsonld')
    ctg_set = ctg_set.union(this_set)
    INDd, this_set = get_data('IND_CleanData/IND_Partial_3.jsonld')
    ctg_set = ctg_set.union(this_set)

    NYTa, this_set = get_data('NYT_CleanData/NYT_Partial_0.jsonld')
    ctg_set = ctg_set.union(this_set)
    NYTb, this_set = get_data('NYT_CleanData/NYT_Partial_1.jsonld')
    ctg_set = ctg_set.union(this_set)
    NYTc, this_set = get_data('NYT_CleanData/NYT_Partial_2.jsonld')
    ctg_set = ctg_set.union(this_set)
    NYTd, this_set = get_data('NYT_CleanData/NYT_Partial_3.jsonld')
    ctg_set = ctg_set.union(this_set)
    NYTe, this_set = get_data('NYT_CleanData/NYT_Partial_4.jsonld')
    ctg_set = ctg_set.union(this_set)
    NYTf, this_set = get_data('NYT_CleanData/NYT_Partial_5.jsonld')
    ctg_set = ctg_set.union(this_set)
    NYTg, this_set = get_data('NYT_CleanData/NYT_Partial_6.jsonld')
    ctg_set = ctg_set.union(this_set)
    NYTh, this_set = get_data('NYT_CleanData/NYT_Partial_7.jsonld')
    ctg_set = ctg_set.union(this_set)

    WPa, this_set = get_data('WP_CleanData/WP_Partial_0.jsonld')
    ctg_set = ctg_set.union(this_set)
    WPb, this_set = get_data('WP_CleanData/WP_Partial_1.jsonld')
    ctg_set = ctg_set.union(this_set)
    WPc, this_set = get_data('WP_CleanData/WP_Partial_2.jsonld')
    ctg_set = ctg_set.union(this_set)
    WPd, this_set = get_data('WP_CleanData/WP_Partial_3.jsonld')
    ctg_set = ctg_set.union(this_set)
    WPe, this_set = get_data('WP_CleanData/WP_Partial_4.jsonld')
    ctg_set = ctg_set.union(this_set)
    WPf, this_set = get_data('WP_CleanData/WP_Partial_5.jsonld')
    ctg_set = ctg_set.union(this_set)
    WPg, this_set = get_data('WP_CleanData/WP_Partial_6.jsonld')
    ctg_set = ctg_set.union(this_set)
    WPh, this_set = get_data('WP_CleanData/WP_Partial_7.jsonld')
    ctg_set = ctg_set.union(this_set)
    WPi, this_set = get_data('WP_CleanData/WP_Partial_8.jsonld')
    ctg_set = ctg_set.union(this_set)
    WPj, this_set = get_data('WP_CleanData/WP_Partial_9.jsonld')
    ctg_set = ctg_set.union(this_set)
    WPk, this_set = get_data('WP_CleanData/WP_Partial_10.jsonld')
    ctg_set = ctg_set.union(this_set)
    WPl, this_set = get_data('WP_CleanData/WP_Partial_11.jsonld')
    ctg_set = ctg_set.union(this_set)"""
    WPm, this_set = get_data('WP_CleanData/WP_Partial_12.jsonld')
    ctg_set = ctg_set.union(this_set)
    WPn, this_set = get_data('WP_CleanData/WP_Partial_13.jsonld')
    ctg_set = ctg_set.union(this_set)

    #articles = np.concatenate((a,b,c,d,e,f,g,h,i,j,k), axis = 0)
    #articles = np.concatenate((WPa, WPb, WPc, WPd, WPe, WPf, WPg, WPh, WPi, WPj, WPk, WPl, WPm, WPn, NYTa, NYTb, NYTc, NYTd, NYTe, NYTf, NYTg, NYTh, INDa, INDb, INDc, INDd, HPa, HPb, HPc, HPd, HPe, HPf, HPg, HPh, HPi, HPj, DMa, DMb, DMc, DMd, DMe, DMf, DMg, DMh, DMi, DMj, DMk), axis=0)
    articles = np.concatenate((WPm, WPn), axis=0)
    # articles = np.array(a)
    return articles, ctg_set


def get_data(dir):

    with open('IONData2016/' + dir) as json_data:
        data = json.load(json_data)

    content = data['@reverse']
    articles = []
    ctg_set = set()
    id_categories = None
    id_annotations = None

    global NO_ANT_CNT
    global NO_CTG_CNT
    global ERR_CNT

    for i in range(0,len(content['publisher'])):
        this_id = content['publisher'][i]['@id']
        this_date = content['publisher'][i]['datePublished']
        try:
            id_categories = content['publisher'][i]['category']
        except Exception as e:
            #print "No categories or annotations for articles " + this_id
            NO_CTG_CNT += 1
        try:
            id_annotations = content['publisher'][i]['about']
        except Exception as e:
            #print "No annotations for article " + this_id
            NO_ANT_CNT += 1

        if id_annotations is None and id_categories is None:
            ERR_CNT += 1
            continue
        elif id_annotations is None:
            id_annotations = id_categories
            id_annotations_t = tuple(id_categories)
        elif id_categories is None:
            id_annotations = id_annotations
            id_annotations_t = tuple(id_annotations)
        else:
            id_annotations = np.array(id_annotations)
            id_annotations_t = tuple(id_annotations)
        articles.append([this_id, this_date, id_annotations])
        for annot in id_annotations_t:
            ctg_set.add(annot)
    articles = np.array(articles, dtype=object)
    return articles, ctg_set


print "Loading data.."
articles, ctg_set = load_data()
ctg_set = sorted(ctg_set)

print "Creating dictionary.."
ctg_to_id = {ctg_set[i]: i for i in range(0,len(ctg_set))}
id_to_ctg = {i:ctg_set[i] for i in range(0,len(ctg_set))}

print "Found " + str(len(articles)) + " articles with " + str(len(ctg_to_id)) + " categories"
print "No annotations for " + str(NO_ANT_CNT) + "articles"
#print "Sample: " + str(articles[0])
print "Creating vectors.."

article_vecs = []
for article in articles:
    article_vec = []
    #print len(article[2])
    for ctg in article[2]:
        if ctg_to_id[ctg] is not None:
            article_vec.append(ctg_to_id[ctg])

    article_vecs.append([article[0],article[1], article_vec])

with open('annotation_vectors.csv', 'wb') as article_vec_out:
    writer = csv.writer(article_vec_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for a_vec in article_vecs:
        writer.writerow(a_vec)

with open('annotation_to_indext.csv', 'wb') as article_dict_out:
    writer = csv.writer(article_dict_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for key, value in ctg_to_id.items():
        writer.writerow([key.encode('utf-8'), value])
