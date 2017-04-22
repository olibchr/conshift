from flask import Flask, request
import jsonify
import csv
import sys
from scipy.stats import entropy
from sklearn.metrics import pairwise as pw
import string
import warnings
import time
import datetime

app = Flask(__name__)

warnings.filterwarnings("ignore")
csv.field_size_limit(sys.maxsize)

# Parse arguments
path = sys.argv[1]
bucketsize = 0
filters = []

# Init global vars
concepts = []
filter_id_to_ctg, all_id_to_ctg, docid_to_date, weights, id_to_con = {}, {}, {}, {}, {}

class Concept():
    def __init__(self, id, name, features):
        self.id = id
        self.name = name
        self.features = features
        self.docID_frames = []
        self.frames = []
        self.vector = []
        self.intervals = []
        self.cosim = []
        self.top_adds = []
        self.top_removals = []
        self.top_core = []
        self.core_set = set()
    def into_timeframes(self):
        tag_quad = [[int(item.split('_')[0]), int(item.split('_')[1]), datetime.datetime.strptime(docid_to_date[int(item.split('_')[1])], "%Y-%m-%d"), 1] for item in self.features]
        tag_quad = sorted(tag_quad, key=lambda date: (date[2], date[1]))
        tag_len = len(set([tag[1] for tag in tag_quad]))
        if tag_len <= 2 * bucketsize: buckets=2
        else: buckets = int(round(tag_len/(1.0 * bucketsize)))
        tmpbucketsize = int(round(tag_len / (1.0 * buckets)))
        all_buckets = [dict() for x in range(buckets)]
        all_last_adds = buckets * [time.strptime("2015-08-14", "%Y-%m-%d")]
        i = 0
        t = 0
        this_bucket = all_buckets[0]
        last_tag_doc = tag_quad[0][1]
        all_tag_docs = []
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
            all_tag_docs.append(tag_doc)
        for this_bucket, last_add in zip(all_buckets, all_last_adds):
            self.docID_frames.append(all_tag_docs)
            self.frames.append([k,v] for k,v in this_bucket.iteritems())
            self.intervals.append(str(last_add)[:10])
        self.intervals = list(set(self.intervals))
    def rebuild_dist(self):
        vlen = len(all_id_to_ctg)
        for d_vec in self.frames:
            d_vector = [0.00001] * vlen
            for keyval in d_vec:
                d_vector[keyval[0]] = keyval[1] * weights[keyval[0]]
            self.vector.append(d_vector)
    def get_cosim(self):
        distr = self.vector
        emptbucks = 0
        for i in range(0,len(distr)-1):
            this_distr = distr[i]
            next_distr = distr[i+1]
            if sum(this_distr) < 1 or sum(next_distr) < 1:
                emptbucks +=1
                self.cosim.append("NaN")
                continue
            this_cnt = [int(i) if i > 0.1 else 0 for i in this_distr]
            next_cnt = [int(i) if i > 0.1 else 0 for i in next_distr]
            additions = [[a[1], idx] if not bool(a[0]) and bool(a[1]) else 0 for idx, a in enumerate(zip(this_cnt, next_cnt))]
            removals = [[a[0], idx] if bool(a[0]) and not bool(a[1]) else 0 for idx, a in enumerate(zip(this_cnt, next_cnt))]
            core = [[a[1],idx] if (bool(a[0]) and bool(a[1])) and idx != self.id else 0 for idx, a in enumerate(zip(this_cnt, next_cnt))]
            top_adds = [[all_id_to_ctg[idx][28:], a] for a, idx in sorted(additions, reverse=True)[:5]]
            top_rem = [[all_id_to_ctg[idx][28:],a] for a, idx in sorted(removals, reverse=True)[:5]]
            top_core = [[all_id_to_ctg[idx][38:],a] for a, idx in sorted(core, reverse=True)[:5]]
            this_entropy = pw.cosine_similarity(this_distr, next_distr)
            self.cosim.append(this_entropy)
            self.top_adds.append(top_adds)
            self.top_removals.append(top_rem)
            self.top_core.append(top_core)
    def pretty_print(self):
        print "Cosine Sim within filter " + self.name + " are: "
        for i in range(len(self.intervals)-1):
            if self.cosim[i] =="NaN": continue
            print "     Window " + self.intervals[i] + " to " + self.intervals[i+1] + ": " + str(self.cosim[i]) \
                  + "  /// Top adds: " + str(self.top_adds[i])  + "  /// Top rems: " + str(self.top_removals[i])  \
                  + "  /// Top core: " + str(self.top_core[i])
    def serialize(self):
        return {
            'intervals':self.intervals,
            'cosim':self.cosim,
            'core':self.top_core,
            'adds':self.top_adds,
            'rems':self.top_removals,
            'docID_frames':self.docID_frames
        }


def get_ctg():
    filter_id_to_ctg = {}
    all_id_to_ctg = {}
    with open(path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            filter_id_to_ctg[int(row[1])] = row[0]
            all_id_to_ctg[int(row[1])] = row[0]
    return filter_id_to_ctg, all_id_to_ctg


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


def load_distr():
    all_d_content = []
    with open(path + 'all_distributions_time.csv') as distr_vec:
        reader = csv.reader(distr_vec, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        all_data = []
        for row in reader:
            all_data.append([int(row[0]),row[1:]])
    for item in all_data:
        tups = []
        for i in range(0,len(item[1])-2,2):
            tups.append(item[1][i])
        this_concept = Concept(item[0], filter_id_to_ctg[item[0]].split('/')[-1],tups)
        all_d_content.append(this_concept)
    return all_d_content


@app.route('/', methods=['GET'])
def concept_analysis():
    global filters, concepts, bucketsize
    filters = [request.args.get('id', 0, type=str)]
    bucketsize = request.args.get('bucketsize',0,type=str)

    concept = concepts[id_to_con[filters[0]]]
    concept.into_timeframes()
    concept.rebuild_dist()
    concept.get_cosim()
    concept.pretty_print()
    return jsonify(concept.serialize()), 200


def main():
    print "Setting filters.. "
    global filter_id_to_ctg, all_id_to_ctg, concepts, docid_to_date, weights, id_to_con
    filter_id_to_ctg, all_id_to_ctg = get_ctg()
    docid_to_date = load_doc_map()
    weights = load_idf_weights()
    concepts = load_distr()
    id_to_con = {k.id:en for en,k in enumerate(concepts)}



if __name__ == "__main__":
    main()
    app.run(host='0.0.0.0', port=5000, debug=True)

