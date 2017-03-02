
import csv
import sys
from scipy.stats import entropy
from sklearn.metrics import pairwise as pw
import string
import warnings
import time
import datetime, random
import ast
warnings.filterwarnings("ignore")

path = sys.argv[1]
csv.field_size_limit(sys.maxsize)


def get_ctg(filters):
    filter_id_to_ctg = {}
    all_id_to_ctg = {}
    with open(path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            if int(row[1]) in filters:
                filter_id_to_ctg[int(row[1])] = row[0]
            all_id_to_ctg[int(row[1])] = row[0]
    return filter_id_to_ctg, all_id_to_ctg


def load_distr(filters):
    all_d_content = []
    with open(path + 'all_distributions_time.csv') as distr_vec:
        reader = csv.reader(distr_vec, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        all_data = []
        for row in reader:
            if int(row[0]) not in filters: continue
            all_data.append([int(row[0]),row[1:]])
            if len(all_data) == len(filters):
                del reader
                break
    for item in all_data:
        tups = []
        for i in range(0,len(item[1])-2,2):
            # change this to
            tups.append((item[1][i], 1))
            #tups.append((item[1][i], int(item[1][i+1])))
        all_d_content.append([item[0], tups])
    return all_d_content


def load_doc_map():
    docid_to_date = {}
    with open(path + 'docid_to_date.csv') as docmap:
        reader = csv.reader(docmap, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            docid_to_date[int(row[0])] = row[1]
    return docid_to_date


def load_idf_weights():
    filter_id_to_weight = {}
    with open(path + "all_distributions_weights.csv") as weights_map:
        reader = csv.reader(weights_map, delimiter=',', quotechar='|',quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            filter_id_to_weight[int(row[0])] = float(row[1])
    return filter_id_to_weight


def randomBuckets(concept, docid_to_date):
    all_frames = []
    tag_quad = [[int(item[0].split('_')[0]), int(item[0].split('_')[1]), datetime.datetime.strptime(docid_to_date[int(item[0].split('_')[1])], "%Y-%m-%d"), 1] for item in concept[1]]
    tag_quad = sorted(tag_quad, key=lambda date: (date[2], date[1]))
    articleTags = []
    lastArticle = tag_quad[0][1]
    thisArticleTagSet = []
    for tag in tag_quad:
        thisArticle = tag[1]
        if thisArticle == lastArticle:
            thisArticleTagSet.append(tag[0])
        else:
            lastArticle = thisArticle
            articleTags.append(thisArticleTagSet)
            thisArticleTagSet = [tag[0]]

    randomSize = 100
    buckets = int(round(len(articleTags)/(1.0 * randomSize)))
    all_buckets = [dict() for x in range(buckets)]

    for bucket in all_buckets:
        for i in range(randomSize):
            randomArticle = articleTags[random.randrange(len(articleTags))]
            for annot in randomArticle:
                if annot in bucket: bucket[annot] += 1
                else: bucket[annot]=1
    for this_bucket in all_buckets:
        all_frames.append([concept[0], [[k,v] for k,v in this_bucket.iteritems()]])
    return all_frames


def rebuild_distr(all_d_content, vlen, weights):
    all_d_vec = []
    for d_vec in all_d_content:
        d_vector = [0.000001] * vlen
        d_id = d_vec[0]
        for keyval in d_vec[1]:
            d_vector[keyval[0]] = keyval[1] * weights[keyval[0]]
        all_d_vec.append([d_id, d_vector])
    return all_d_vec


# might be problem: distributions might not contain a specific vector --> need identifier
def kl_div(distr, all_id_to_ctg):
    all_div = []
    emptbucks = 0
    for i in range(0,len(distr)-1):
        this_distr = distr[i][1]
        next_distr = distr[i+1][1]
        if sum(this_distr) < 1 or sum(next_distr) < 1:
            emptbucks +=1
            all_div.append('NaN')
            continue
        this_cnt = [int(i) if i > 0.1 else 0 for i in this_distr]
        next_cnt = [int(i) if i > 0.1 else 0 for i in next_distr]
        changes = [[a[1], idx] if not bool(a[0]) and bool(a[1]) else 0 for idx, a in enumerate(zip(this_cnt, next_cnt))]
        top_change = [all_id_to_ctg[idx][28:] for a, idx in sorted(changes, reverse=True)[:5]]
        this_entropy = pw.cosine_similarity(this_distr, next_distr)
        all_div.append(this_entropy)
    all_div.append(pw.cosine_similarity(distr[0][1], distr[len(distr)-1][1]))
    print '     ' + str(emptbucks) + ' empty buckets in ' + str(distr[0][0])
    return all_div



def main(argv):
    bucketsize = int(argv[2])
    filters = map(int, argv[3:])
    weights = load_idf_weights()
    docid_to_date = load_doc_map()
    print "Bucketsize of " + str(bucketsize)
    print "Setting filters.. "
    filter_id_to_ctg, all_id_to_ctg = get_ctg(filters)
    distributions = load_distr(filters)
    for filter in filters:
        for idx in range(len(distributions)):
            if distributions[idx][0] == filter:
                print "     " + str(filter) + ": " + str(filter_id_to_ctg[filter].split('/')[-1]) + " with " + str(len(distributions[idx][1])) + ' annotations in ' + str(len(set(item[0].split('_')[1] for item in distributions[idx][1]))) + ' articles.'


    print "Create sparse vectors"
    for i in range(0,len(distributions)):
        concept = randomBuckets(distributions[i], docid_to_date)
        distributions[i] = rebuild_distr(concept, len(all_id_to_ctg), weights)
        print "     " + str(filters[i]) + ": Built " + str(len(distributions[i])) + " probability density vectors"

    divergences_per_id = []
    for distribution in distributions:
        divergences_per_id.append(kl_div(distribution, all_id_to_ctg))

    cosineSum = 0
    for i in range(0,len(filters)):
        print "KL Divergences within filter " + str(filter_id_to_ctg[filters[i]].split('/')[-1]) + " are: "
        for k in range(len(divergences_per_id[i])-1):
            if divergences_per_id[i][k][0] == 'NaN':
                continue
            cosineSum +=divergences_per_id[i][k][0]
            #print "     Window " + str(distributions[i][k][2])[:10] + " to " + str(distributions[i][k+1][2])[:10] + ": " + str(("%.5f" % divergences_per_id[i][k][0])) + "  /// Sum of changes: " + str((divergences_per_id[i][k][1]))
        print cosineSum/len(divergences_per_id)
        print ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: enter one or several indices from the dictionary hinting at wikipedia annotations which are preferably related. This program calculates the cosine similarity between the first entered index and all other entered indeces."
    else:
        main(sys.argv)
