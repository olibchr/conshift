import csv, operator
import sys, time, string
from sklearn.feature_extraction.text import TfidfTransformer
from scipy.sparse import lil_matrix
from sklearn.preprocessing import normalize

if len(sys.argv) < 2:
    print "Give dir path to annotion files!"
    exit()
path = sys.argv[1]
quarters = [time.strptime("2014-11-13", "%Y-%m-%d"), time.strptime("2015-02-13", "%Y-%m-%d"), time.strptime("2015-05-13", "%Y-%m-%d"), time.strptime("2015-08-13", "%Y-%m-%d")]


def get_ctg():
    all_id_to_ctg = {}
    with open(path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_id_to_ctg[int(row[1])] = row[0]
    return all_id_to_ctg, all_id_to_ctg


def get_items():
    all_annotations_id = []
    all_annotations_doc = []
    with open(path + 'annotation_vectors.csv') as annotation_vectors:
        reader = csv.reader(annotation_vectors, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        last_id = 0
        this_id_list = []
        last_doc = ''
        this_doc_list = []
        for item in reader:
            this_id = int(item[0])
            if last_id == this_id:
                this_id_list.append([int(item[0]), item[1], time.strptime(item[2], "%Y-%m-%d")])
            else:
                all_annotations_id.append(this_id_list)
                last_id = this_id
                this_id_list = []
                this_id_list.append([int(item[0]), item[1], time.strptime(item[2], "%Y-%m-%d")])

            this_doc = item[1]
            if last_doc == this_doc:
                this_doc_list.append([item[1], int(item[0]), time.strptime(item[2], "%Y-%m-%d")])
            else:
                all_annotations_doc.append(this_doc_list)
                last_doc = this_doc
                this_doc_list = []
                this_doc_list.append([item[1], int(item[0]), time.strptime(item[2], "%Y-%m-%d")])
    return all_annotations_id[1:], sorted(all_annotations_doc[1:], key=lambda docid: docid[0])


def build_vectors(all_annotations_id, all_annotations_doc):
    i = 0
    all_d_vector = []
    for ids in all_annotations_id:
        if i % 500 == 0:
            print "progress: " + str(i) + ", " + str(len(all_annotations_id)) + ", " + str(
                (i * 100) / float(1.0 * len(all_annotations_id))) + "%"
        i += 1
        vector = {}
        indeces = []
        for item in ids:
            docid = item[1]
            #print item
            for doc in all_annotations_doc:
                if doc[0][0] == docid:
                    for doc_w_docid in doc:
                        if doc_w_docid[1] in vector.keys():
                            vector[doc_w_docid[1]] = vector[doc_w_docid[1]] + 1
                        else:
                            vector[doc_w_docid[1]] = 1
                    break
            for k, v in vector.iteritems():
                indeces.append([k, v])
        print ids
        print indeces
        all_d_vector.append([int(ids), indeces])
    return all_d_vector


def build_sparse(all_d_content, lilx, lily):
    positions = []
    data = []
    for distr in all_d_content:
        this_position = []
        this_data = []
        for tuple in distr[1]:
            if tuple[0] == '' or tuple[1] == '':
                continue
            this_position.append(tuple[0])
            this_data.append(tuple[1])
        positions.append(this_position)
        data.append(this_data)
    sparse_entities = lil_matrix((lilx, lily))
    sparse_entities.rows = positions
    sparse_entities.data = data
    sparse_entities.tocsr()
    return sparse_entities


print "Loading Items"
all_annotations_id, all_annotations_doc = get_items()
print "Building Distributions"
all_d_vecs = build_vectors(all_annotations_id, all_annotations_doc)


