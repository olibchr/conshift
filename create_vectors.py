import json
#from pyLD import jsonld
import numpy as np
import csv


NO_ANT_CNT = 0
NO_CTG_CNT = 0
ERR_CNT = 0
all_abouts = []

def load_data():
    #load the data from the directories
    ctg_set = set()

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
    ctg_set = ctg_set.union(this_set)
    WPm, this_set = get_data('WP_CleanData/WP_Partial_12.jsonld')
    ctg_set = ctg_set.union(this_set)
    WPn, this_set = get_data('WP_CleanData/WP_Partial_13.jsonld')
    ctg_set = ctg_set.union(this_set)

    articles = np.concatenate((WPa, WPb, WPc, WPd, WPe, WPf, WPg, WPh, WPi, WPj, WPk, WPl, WPm, WPn, NYTa, NYTb, NYTc, NYTd, NYTe, NYTf, NYTg, NYTh, INDa, INDb, INDc, INDd, HPa, HPb, HPc, HPd, HPe, HPf, HPg, HPh, HPi, HPj, DMa, DMb, DMc, DMd, DMe, DMf, DMg, DMh, DMi, DMj, DMk), axis=0)
    #articles = np.concatenate((WPm, WPn), axis=0)
    # articles = np.array(a)
    return articles, ctg_set


def get_data(dir):
    # get the data
    with open('IONData2016/' + dir) as json_data:
        data = json.load(json_data)

    content = data['@reverse']
    articles = []
    ctg_set = set()
    id_categories = None
    id_abouts = None

    global NO_ANT_CNT
    global NO_CTG_CNT
    global ERR_CNT
    global all_abouts

    # filter the data for category and about annotations
    for i in range(0,len(content['publisher'])):
        this_id = content['publisher'][i]['@id']
        this_date = content['publisher'][i]['datePublished']

        try:
            id_categories = content['publisher'][i]['category']
        except Exception as e:
            NO_CTG_CNT += 1

        try:
            id_abouts = content['publisher'][i]['about']
            for i in range(0,len(id_abouts)):
                about = id_abouts[i]
                if 'wiki/wiki' in about:
                    id_abouts[i] = about.replace('wiki/wiki', 'wiki')
            all_abouts.append(id_abouts)
        except Exception as e:
            #print "No annotations for article " + this_id
            NO_ANT_CNT += 1

        if id_abouts is None and id_categories is None:
            ERR_CNT += 1
            continue
        elif id_abouts is None:
            id_annotations = id_categories
        elif id_categories is None:
            id_annotations = id_abouts
        else:
            id_annotations = np.array(id_abouts)
            id_annotations = np.append(id_annotations, id_categories)

        id_annotations_t = tuple(id_annotations)
        articles.append([this_id, this_date, id_annotations])
        for annot in id_annotations_t:
            ctg_set.add(annot)
    articles = np.array(articles, dtype=object)
    return articles, ctg_set


print "Loading data.." # we load the data
articles, ctg_set = load_data()
ctg_set = sorted(ctg_set)

#for item in ctg_set:
#    if 'wiki/wiki' in item:
#        item.replace('wiki/wiki','wiki')

print "Creating dictionary.." # put all annotations into dictionaries
ctg_to_id = {ctg_set[i]: i for i in range(0,len(ctg_set))}
id_to_ctg = {i:ctg_set[i] for i in range(0,len(ctg_set))}

print "Found " + str(len(articles)) + " articles with " + str(len(ctg_to_id)) + " categories"
print "No about annotations for " + str(NO_ANT_CNT) + "articles." + " No ctg annotations for " + str(NO_CTG_CNT) + "articles."
print "Creating vectors.."

# we build annotation vectors which contain the index of a positive entry (=1), rest is 0
article_vecs = []
annot_cnt = 0
for article in articles:
    article_vec = []
    for ctg in article[2]:
        if ctg_to_id[ctg] is not None:
            article_vec.append(ctg_to_id[ctg])
            annot_cnt += 1

    article_vecs.append([article[0],article[1], article_vec])
print "avg:" + str(annot_cnt / len(articles)) + " cnts: " + str(annot_cnt) + " len " + str(len(articles))

with open('annotation_vectors.csv', 'wb') as article_vec_out:
    writer = csv.writer(article_vec_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for a_vec in article_vecs:
        writer.writerow(a_vec)

with open('annotation_to_index.csv', 'wb') as article_dict_out:
    writer = csv.writer(article_dict_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for key, value in ctg_to_id.items():
        writer.writerow([key.encode('utf-8'), value])

"""
with open('about_to_index.csv', 'wb') as abouts_dict:
    writer = csv.writer(abouts_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    all_abouts_t = tuple(all_abouts)
    abouts_set = set()
    for about in all_abouts_t:
        abouts_set.add(about)
    abouts_set = sorted(abouts_set)
    annot_to_id = {abouts_set[i] : ctg_to_id[abouts_set[i]] for i in range(0,len(abouts_set))}
    for k,v in annot_to_id.items():
        writer.writerow([key.encode('utf-8'), v])
"""
