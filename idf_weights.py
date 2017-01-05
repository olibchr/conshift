import csv
import sys
import numpy as np
import pickle
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfTransformer
from scipy.sparse import lil_matrix
from itertools import izip

"""
This program computes tf-idf scores based on density vectors, created by distr_vec for all density distributions of annotations.
"""
csv.field_size_limit(sys.maxsize)
path = sys.argv[1]
def load_distr():
    all_d_content = []
    with open(path + 'all_distributions.csv') as distr_vec:
        reader = csv.reader(distr_vec, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            features = [int(k.replace('[','').replace(']','').replace(" ","").replace("'","")) for k in row[1].split(",")]
            l_features = [features[x] for x in range(0,len(features),2)]
            xy_features = [(k,v) for k,v in {l_features[y/2-1]:features[y] for y in range(1,len(features),2)}.items()]
            all_d_content.append([int(row[0]),xy_features])
    return all_d_content


def get_ctg():
    all_id_to_ctg = {}
    all_ctg_to_id = {}
    with open(path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_id_to_ctg[int(row[1])] = row[0]
            all_ctg_to_id[row[0]] = int(row[1])
    return all_ctg_to_id, all_id_to_ctg


def build_sparse(all_d_content, lilx, lily):
    positions = []
    data = []
    for distr in all_d_content:
        this_position = []
        this_data = []
        for tuple in distr[1]:
            this_position.append(tuple[0])
            this_data.append(tuple[1])
        positions.append(this_position)
        data.append(this_data)

    sparse_entities = lil_matrix((lilx, lily))
    sparse_entities.rows = positions
    sparse_entities.data = data
    sparse_entities.tocsr()
    return sparse_entities


def build_all_idf(all_d_vec):
    transformer = TfidfTransformer(smooth_idf=False)
    sparse_entities = transformer.fit_transform(all_d_vec)
    return sparse_entities


def main():
    all_d_content = load_distr()
    all_ctg_to_id, all_id_to_ctg = get_ctg()
    print "Create sparse vectors"
    all_d_vec = build_sparse(all_d_content, len(all_d_content), len(all_id_to_ctg))

    print "Inverse Document Frequency"
    #all_d_vec = rebuild_distr(all_d_content)
    sparse_entities = build_all_idf(all_d_vec)

    print "Results: " + str(len(sparse_entities))

    with open('all_distr_weighted', 'wb') as outfile:
        pickle.dump(sparse_entities, outfile, pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    main()