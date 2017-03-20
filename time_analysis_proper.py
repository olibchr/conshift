import csv
import sys
from scipy.stats import entropy
from sklearn.metrics import pairwise as pw
import string
import warnings
import time
import datetime
from itertools import chain
import ast
warnings.filterwarnings("ignore")
csv.field_size_limit(sys.maxsize)

# Parse arguments
path = sys.argv[1]
bucketsize = int(sys.argv[2])
filters = map(int, sys.argv[3:])

# Init global vars
concepts = []
filter_id_to_ctg, all_id_to_ctg, docid_to_date, weights = {}, {}, {}, {}


class Concept():
    def __init__(self, id, name, features):
        self.id = id
        self.name = name
        self.features = features
        self.frames = []
        self.vector = []
        self.intervals = []
        self.cosim = []
        self.top_adds = []
        self.top_removals = []
        self.top_core = []

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
            self.frames.append([k,v] for k,v in this_bucket.iteritems())
            self.intervals.append(str(last_add)[:10])

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
            top_core = [[all_id_to_ctg[idx][28:],a] for a, idx in sorted(core, reverse=True)[:5]]
            this_entropy = pw.cosine_similarity(this_distr, next_distr)
            self.cosim.append(this_entropy)
            self.top_adds.append(top_adds)
            self.top_removals.append(top_rem)
            self.top_core.append(top_core)


def get_ctg():
    filter_id_to_ctg = {}
    all_id_to_ctg = {}
    with open(path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            if int(row[1]) in filters:
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
            tups.append(item[1][i])
            #tups.append((item[1][i], int(item[1][i+1])))
        this_concept = Concept(item[0], filter_id_to_ctg[item[0]].split('/')[-1],tups)
        print "     " + str(this_concept.id) + ": " + this_concept.name + " with " + str(len(this_concept.features)) + ' annotations in ' + str(len(set(item.split('_')[1] for item in this_concept.features))) + ' articles.'
        all_d_content.append(this_concept)
    return all_d_content


def pretty_print():
    for concept in concepts:
        print "Cosine Sim within filter " + concept.name + " are: "
        for i in range(len(concept.intervals)-1):
            if concept.cosim[i] =="NaN": continue
            print "     Window " + concept.intervals[i] + " to " + concept.intervals[i+1] + ": " + str(concept.cosim[i]) \
                  + "  /// Top adds: " + str(concept.top_adds[i])  + "  /// Top rems: " + str(concept.top_removals[i])  \
                  + "  /// Top core: " + str(concept.top_core[i])


def save_state():
    with open('2_results/analysis_results_' + ''.join(map(str,filters)) + '.csv', 'wb') as out:
        writer = csv.writer(out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for con in concepts:
            for i in range(len(con.intervals)-1):
                flat_topcore = [val for sublist in con.top_core[i] for val in sublist]
                flat_topadds = [val for sublist in con.top_adds[i] for val in sublist]
                flat_toprems = [val for sublist in con.top_adds[i] for val in sublist]
                print_list = [con.id, con.name, con.intervals[i], con.cosim[i][0][0]] + flat_topcore + flat_topadds + flat_toprems
                writer.writerow(print_list)
            """flat_topcore = [val for sublist in [con.top_core[j] for j in range(len(con.top_core)-1)] for val in sublist]
            print con.top_core
            print flat_topcore
            flat_topadds = [val for sublist in [con.top_adds[j] for j in range(len(con.top_adds)-1)] for val in sublist]
            flat_toprems = [val for sublist in [con.top_removals[j] for j in range(len(con.top_removals)-1)] for val in sublist]
            flat_tp = [val for sublist in [[con.intervals[i], con.cosim[i][0][0], con.top_core[i], con.top_adds, con.top_removals] for i in range(len(con.intervals)-1)] for val in sublist]
            printlist = [con.id, con.name] + flat_tp #+ flat_topcore + flat_topadds + flat_toprems
            writer.writerow(printlist)"""



def main():
    print "Setting filters.. "
    global filter_id_to_ctg, all_id_to_ctg, concepts, docid_to_date, weights
    filter_id_to_ctg, all_id_to_ctg = get_ctg()
    docid_to_date = load_doc_map()
    weights = load_idf_weights()
    concepts = load_distr(filters)

    print "Building Concepts"
    for concept in concepts:
        concept.into_timeframes()
        concept.rebuild_dist()
        concept.get_cosim()
    pretty_print()
    save_state()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Not enough arguments"
    else:
        main()


