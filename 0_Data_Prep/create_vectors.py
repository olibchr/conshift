import json
#from pyLD import jsonld
import numpy as np
import csv
import sys, os, operator

"""
The purpose of this program is to load the json data from the 2014/2015 newspaper article data set and
to filter the annotations and abouts per article.
The output is a csv file of all articles and their annotations as ID's. A second file will be produced which maps the
IDs to annotations.

"""

NO_ANT_CNT = 0
NO_CTG_CNT = 0
ERR_CNT = 0
all_abouts = []

path = sys.argv[1]
def load_data():
    #load the data from the directories
    ctg_set = set()

    for filename in os.listdir(path):
        if ".jsonld" not in filename:
            continue
        print filename
        this_article, this_set = get_data(path + filename)
        if 'articles' in locals():
            articles = np.concatenate((articles, this_article), axis=0)
        else:
            articles = this_article
        ctg_set = ctg_set.union(this_set)
    return articles, ctg_set


def get_data(dir):
    # get the data
    with open(dir) as json_data:
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
                    id_abouts[i] = about.replace('wiki/wiki/', 'wiki/')
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


def format(articles, ctg_to_id):
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
    return article_vecs


def invert_items(all_items, filter, all_id_to_ctg):
    index_cnt = {key: 0 for key in filter}
    inverted_items = []

    for item in all_items:
        for annot in item[2]:
            annot = int(annot)
            inverted_items.append([annot, item])
            index_cnt[annot] = index_cnt[annot] + 1
    sorted_index_cnt = sorted(index_cnt.items(), key=operator.itemgetter(1), reverse=True)
    kill_set = []
    for key in sorted_index_cnt:
        if key[1] == 1:
            kill_set.append(key[0])

    sorted(inverted_items, key=lambda key: inverted_items[0])
    return kill_set


def cleanse_concepts(kill_set, article_vecs, ctg_to_id):
    clean_items = []
    clean_dict = {}
    i = 0
    for article_vec in article_vecs:
        if i % 1000 == 0:
            print "progress: " + str(i) + ", " + str(len(article_vecs)) + ", " + str(
                (i * 100) / float(1.0 * len(article_vecs))) + "%"
        i += 1

        if article_vec[0] in kill_set:
            continue
        this_annot = []
        for annot in article_vec[2]:
            if annot in kill_set:
                continue
            else:
                this_annot.append(annot)
        clean_items.append([article_vec[0], article_vec[1], this_annot])

    for did in ctg_to_id.keys():
        if did in kill_set:
            continue
        else:
            clean_dict[did] = ctg_to_id[did]

    return clean_items, clean_dict



def main():
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
    print "No about annotations for " + str(NO_ANT_CNT) + " articles." + " No ctg annotations for " + str(NO_CTG_CNT) + " articles."
    print "Creating vectors.."

    article_vecs = format(articles, ctg_to_id)

    kill_set = invert_items(article_vecs, [x for x in id_to_ctg.keys()], id_to_ctg)

    print "Erasing " + str(len(kill_set)) + " concepts which appear only once!"

    del id_to_ctg
    article_vecs, ctg_to_id = cleanse_concepts(kill_set, article_vecs, ctg_to_id)

    with open('annotation_vectors.csv', 'wb') as article_vec_out:
        writer = csv.writer(article_vec_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for a_vec in article_vecs:
            writer.writerow(a_vec)

    with open('annotation_to_index.csv', 'wb') as article_dict_out:
        writer = csv.writer(article_dict_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for key, value in ctg_to_id.items():
            writer.writerow([key.encode('utf-8'), value])



if __name__ == "__main__":
    main()


