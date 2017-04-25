import csv
import sys
from sklearn.metrics import pairwise as pw
import warnings
import datetime
import matplotlib.pyplot as plt
import numpy as np
warnings.filterwarnings("ignore")
csv.field_size_limit(sys.maxsize)

# Parse arguments
path = sys.argv[2]
st_path = sys.argv[1]
filters = map(int, sys.argv[3:])

# Init global vars
concepts = []
filter_id_to_ctg, all_id_to_ctg, docid_to_date, weights = {}, {}, {}, {}


class Concept:
    def __init__(self, publisher, id, name, features):
        self.publisher = publisher
        self.id = id
        self.name = name
        self.features = features
        self.frames = []
        self.vector = []
        self.cosim = []
        self.top_uncommon = []
        self.top_common = []
    def into_frame(self):
        tag_quad = [[int(item.split('_')[0]), int(item.split('_')[1]), datetime.datetime.strptime(docid_to_date[int(item.split('_')[1])], "%Y-%m-%d"), 1] for item in self.features]
        tag_quad = sorted(tag_quad, key=lambda date: (date[2], date[1]))
        this_bucket = {}
        all_tag_docs = []
        for tag in tag_quad:
            tag_id = tag[0]
            tag_doc = tag[1]
            tag_cnt = tag[3]
            if tag_id in this_bucket:
                this_bucket[tag_id] = this_bucket[tag_id] + tag_cnt
            else:
                this_bucket[tag_id] = tag_cnt
            all_tag_docs.append(tag_doc)
        self.frames.append([k,v] for k,v in this_bucket.iteritems())
    def rebuild_dist(self):
        vlen = len(all_id_to_ctg)
        for d_vec in self.frames:
            d_vector = [0.00001] * vlen
            for keyval in d_vec:
                d_vector[keyval[0]] = keyval[1] * weights[keyval[0]]
            self.vector = d_vector


def get_ctg():
    filter_id_to_ctg = {}
    all_id_to_ctg = {}
    with open(st_path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            if int(row[1]) in filters:
                filter_id_to_ctg[int(row[1])] = row[0]
            all_id_to_ctg[int(row[1])] = row[0]
    return filter_id_to_ctg, all_id_to_ctg


def load_doc_map():
    docid_to_date = {}
    with open(st_path + 'docid_to_date.csv') as docmap:
        reader = csv.reader(docmap, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            docid_to_date[int(row[0])] = row[1]
    return docid_to_date


def load_idf_weights():
    filter_id_to_weight = {}
    with open(st_path + "all_distributions_weights.csv") as weights_map:
        reader = csv.reader(weights_map, delimiter=',', quotechar='|',quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            filter_id_to_weight[int(row[0])] = float(row[1])
    return filter_id_to_weight


def load_distr(filters):
    all_d_content = []
    with open(path + 'WP_distributions_time.csv') as distr_vec:
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
            tups.append(item[1][i])
        this_concept = Concept('WP', item[0], filter_id_to_ctg[item[0]].split('/')[-1],tups)
        print "     WP: " + str(this_concept.id) + ": " + this_concept.name + " with " + str(len(this_concept.features)) + ' annotations in ' + str(len(set(item.split('_')[1] for item in this_concept.features))) + ' articles.'
        all_d_content.append(this_concept)
    with open(path + 'HP_distributions_time.csv') as distr_vec:
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
            tups.append(item[1][i])
        this_concept = Concept('HP', item[0], filter_id_to_ctg[item[0]].split('/')[-1],tups)
        print "     HP: " + str(this_concept.id) + ": " + this_concept.name + " with " + str(len(this_concept.features)) + ' annotations in ' + str(len(set(item.split('_')[1] for item in this_concept.features))) + ' articles.'
        all_d_content.append(this_concept)

    with open(path + 'NYT_distributions_time.csv') as distr_vec:
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
            tups.append(item[1][i])
        this_concept = Concept('NYT', item[0], filter_id_to_ctg[item[0]].split('/')[-1],tups)
        print "     NYT: " + str(this_concept.id) + ": " + this_concept.name + " with " + str(len(this_concept.features)) + ' annotations in ' + str(len(set(item.split('_')[1] for item in this_concept.features))) + ' articles.'
        all_d_content.append(this_concept)

    with open(path + 'DM_distributions_time.csv') as distr_vec:
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
            tups.append(item[1][i])
        this_concept = Concept('DM', item[0], filter_id_to_ctg[item[0]].split('/')[-1],tups)
        print "     DM: " + str(this_concept.id) + ": " + this_concept.name + " with " + str(len(this_concept.features)) + ' annotations in ' + str(len(set(item.split('_')[1] for item in this_concept.features))) + ' articles.'
        all_d_content.append(this_concept)

    with open(path + 'IND_distributions_time.csv') as distr_vec:
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
            tups.append(item[1][i])
        this_concept = Concept('IND', item[0], filter_id_to_ctg[item[0]].split('/')[-1],tups)
        print "     IND: " + str(this_concept.id) + ": " + this_concept.name + " with " + str(len(this_concept.features)) + ' annotations in ' + str(len(set(item.split('_')[1] for item in this_concept.features))) + ' articles.'
        all_d_content.append(this_concept)

    return all_d_content


def get_similarities():
    for con in concepts:
        for ccon in concepts:
            if con.publisher == ccon.publisher:
                con.cosim.append(0)
                con.top_uncommon.append(" ")
                con.top_common.append(" ")
                continue
            con.cosim.append(pw.cosine_similarity(con.vector, ccon.vector))
            con_cnt = [int(i) if i > 0.1 else 0 for i in con.vector]
            ccon_cnt = [int(i) if i > 0.1 else 0 for i in ccon.vector]
            additions = [[a[1], idx] if not bool(a[0]) and bool(a[1]) else 0 for idx, a in enumerate(zip(con_cnt, ccon_cnt))]
            common = [[a[1],idx] if (bool(a[0]) and bool(a[1])) and idx != con.id else 0 for idx, a in enumerate(zip(con_cnt, ccon_cnt))]
            top_adds = [[all_id_to_ctg[idx][28:], a] for a, idx in sorted(additions, reverse=True)[:5]]
            top_common = [[all_id_to_ctg[idx][38:],a] for a, idx in sorted(common, reverse=True)[:5]]
            con.top_uncommon.append(top_adds)
            con.top_common.append(top_common)


def pretty_print():
    for concept in concepts:
        print "Publisher " + concept.publisher + ": Cosine Sim within filter " + concept.name + " are: "
        for i in range(len(concepts)):
            print "     " + concepts[i].publisher + ": " + str(concept.cosim[i])
    print ""
    print "Details: "
    for c in concepts:
        print "Publisher " + c.publisher + ": "
        for i in range(len(concepts)):
            print "     In Common with " + concepts[i].publisher + ": "  + str(c.top_common[i])
            print "     Not in Common with " + concepts[i].publisher + ": " + str(c.top_uncommon[i])

def mat_plot(concepts):
    """Make a matrix with all zeros and increasing elements on the diagonal"""
    aa = np.zeros((len(concepts),len(concepts)))
    for i in range(len(concepts)):
        for j in range(len(concepts[i].cosim)):
            aa[i, j] = concepts[i].cosim[j]
    return aa


def main():
    print "Setting filters.. "
    global filter_id_to_ctg, all_id_to_ctg, concepts, docid_to_date, weights
    filter_id_to_ctg, all_id_to_ctg = get_ctg()
    docid_to_date = load_doc_map()
    weights = load_idf_weights()
    concepts = load_distr(filters)
    print "Building Concepts"
    for concept in concepts:
        concept.into_frame()
        concept.rebuild_dist()
    get_similarities()
    pretty_print()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(mat_plot(concepts))
    fig.colorbar(cax)
    ax.set_xticklabels(['']+[c.publisher for c in concepts])
    ax.set_yticklabels(['']+[c.publisher for c in concepts])
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Not enough arguments"
    else:
        main()


