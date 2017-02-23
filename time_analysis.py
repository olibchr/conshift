
import csv
import sys
from scipy.stats import entropy
from sklearn.metrics import pairwise as pw
import string
import warnings
import time
import datetime
import ast
warnings.filterwarnings("ignore")

"""
The purpose of this program is to do an investigation of the data which was produced with the create vectors tool.
You have to specify one or several IDs of annotations to investigate about (ID mapping can be found in separate csv file,
produce by create vector tool as well)
In detail, this tool creates density distribution vectors for the specified annotations and compares them to each other
 with a KL divergence / cosine metric to measure similarity.
 All output will be printed on screen.
"""
path = sys.argv[1]
csv.field_size_limit(sys.maxsize)

q_char = '|'


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


def load_idf_weights(filters):
    filter_id_to_weight = {}
    with open(path + "all_distribution_weights.csv") as weights_map:
        reader = csv.reader(weights_map, delimiter=',', quotechar='|',quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            if row[0] in filters:
                filter_id_to_weight[row[0]] = row[1]
    return filter_id_to_weight


def timeframes(concept, bucketsize, docid_to_date):
    all_frames = []
    tag_quad = [[int(item[0].split('_')[0]), int(item[0].split('_')[1]), datetime.datetime.strptime(docid_to_date[int(item[0].split('_')[1])], "%Y-%m-%d"), 1] for item in concept[1]]
    tag_quad = sorted(tag_quad, key=lambda date: (date[2], date[1]))
    tag_len = len(set([tag[1] for tag in tag_quad]))
    #print len(tag_quad)
    #print tag_len
    if tag_len <= 2 * bucketsize:
        buckets=2
    else:
        buckets = int(round(tag_len/(1.0 * bucketsize)))
    tmpbucketsize = int(round(tag_len / (1.0 * buckets)))
    #print tmpbucketsize
    all_buckets = [dict() for x in range(buckets)]
    all_last_adds = buckets * [time.strptime("2015-08-14", "%Y-%m-%d")]
    i = 0
    t = 0
    this_bucket = all_buckets[0]
    last_tag_doc = tag_quad[0][1]
    for tag in tag_quad:
        tag_id = tag[0]
        tag_doc = tag[1]
        tag_date = tag[2]
        tag_cnt = tag[3]
        if i > tmpbucketsize:
            i = 0
            t += 1
            this_bucket = all_buckets[t]
        all_last_adds[t] = tag_date
        if last_tag_doc != tag_doc:
            i+=1
            last_tag_doc = tag_doc
        if tag_id in this_bucket:
            this_bucket[tag_id] = this_bucket[tag_id] + tag_cnt
        else:
            this_bucket[tag_id] = tag_cnt
    for this_bucket, last_add in zip(all_buckets, all_last_adds):
        all_frames.append([concept[0], [[k,v] for k,v in this_bucket.iteritems()], last_add])
    return all_frames


def rebuild_distr(all_d_content, vlen):
    vlen = 111953
    all_d_vec = []
    for d_vec in all_d_content:
        d_vector = [0.000001] * vlen
        d_id = d_vec[0]
        for keyval in d_vec[1]:
            d_vector[keyval[0]] = keyval[1]
        #print "     " + str(sum(d_vector))
        all_d_vec.append([d_id, d_vector, d_vec[2]])
    return all_d_vec


# might be problem: distributions might not contain a specific vector --> need identifier
def kl_div(distr):
    all_div = []
    emptbucks = 0
    for i in range(0,len(distr)-1):
        this_distr = distr[i][1]
        next_distr = distr[i+1][1]
        if sum(this_distr) < 1 or sum(next_distr) < 1:
            emptbucks +=1
            #print "Cant compare quarter " + str(i+1) + " to " + str(i+2) + ". One Vector empty: " + str(sum(this_distr)) + " or " + str(sum(next_distr))
            all_div.append('NaN')
            continue
        #this_entropy = entropy(this_distr, next_distr)
        this_cnt = [1 if i > 0.1 else 0 for i in this_distr]
        next_cnt = [1 if i > 0.1 else 0 for i in next_distr]
        changes = [1 if a ^ b else 0 for a, b in zip(this_cnt, next_cnt)]
        this_entropy = pw.cosine_similarity(this_distr, next_distr)
        all_div.append([this_entropy, [sum(this_cnt), sum(next_cnt), sum(changes)]])
    #all_div.append(entropy(distr[0][1], distr[len(distr)-1][1]))
    all_div.append(pw.cosine_similarity(distr[0][1], distr[len(distr)-1][1]))
    print '     ' + str(emptbucks) + ' empty buckets in ' + str(distr[0][0])
    return all_div


def validation_scoring(distributions):
    scoring = [0] * len(distributions)
    gold_standard = distributions[0]
    k = 0
    for d in distributions:
        for i in range(0,len(d[1])):
            if (d[1][i] >= 0.00001) and (gold_standard[1][i] >= 0.00001):
                scoring[k] += 1
        k += 1
    return scoring


def main(argv):
    bucketsize = int(argv[2])
    filters = map(int, argv[3:])
    print "Bucketsize of " + str(bucketsize)
    print "Setting filters.. "

    filter_id_to_ctg, all_id_to_ctg = get_ctg(filters)

    distributions = load_distr(filters)
    for filter in filters:
        for idx in range(len(distributions)):
            if distributions[idx][0] == filter: print "     " + str(filter) + ": " + str(filter_id_to_ctg[filter].split('/')[-1]) + " with " + str(len(distributions[idx][1])) + ' annotations in ' + str(len(set(item[0].split('_')[1] for item in distributions[idx][1]))) + ' articles.'


    docid_to_date = load_doc_map()

    print "Create sparse vectors"
    for i in range(0,len(distributions)):
        concept = timeframes(distributions[i], bucketsize, docid_to_date)
        distributions[i] = rebuild_distr(concept, len(all_id_to_ctg))
        print "     " + str(filters[i]) + ": Built " + str(len(distributions[i])) + " probability density vectors"

    divergences_per_id = []
    for distr in distributions:
        divergences_per_id.append(kl_div(distr))

    for i in range(0,len(filters)):
        print "KL Divergences within filter " + str(filter_id_to_ctg[filters[i]].split('/')[-1]) + " are: "
        for k in range(len(divergences_per_id[i])-1):
            if divergences_per_id[i][k][0] == 'NaN':
                continue
            print "     Window " + str(distributions[i][k][2])[:10] + " to " + str(distributions[i][k+1][2])[:10] + ": " + str(("%.2f" % divergences_per_id[i][k][0])) + "  /// Sum of changes: " + str((divergences_per_id[i][k][1]))
        print ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: enter one or several indices from the dictionary hinting at wikipedia annotations which are preferably related. This program calculates the cosine similarity between the first entered index and all other entered indeces."
    else:
        main(sys.argv)
