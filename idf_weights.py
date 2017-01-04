import csv
import sys
import numpy as np
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
            features = [k.replace('"', '').replace('[','').replace(']','') for k in row[1].split(',')]
            all_d_content.append([int(row[0]), features])
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


def rebuild_distr(all_d_content):
    all_d_vec = np.array()
    for d_vec in all_d_content:
        d_vector = [0] * len(all_d_content)
        d_id = d_vec[0]
        for keyval in d_vec[1]:
            d_vector[keyval[0]] = keyval[1]
        all_d_vec = np.append(all_d_vec, [d_id, d_vector], axis=0)
    return all_d_vec


def build_sparse(all_d_content, lilx, lily):
    positions = []
    data = []
    for distr in all_d_content:
        print distr
        exit()
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
    return transformer.idf_


def main():
    all_d_content = load_distr()
    all_ctg_to_id, all_id_to_ctg = get_ctg()
    print "Create sparse vectors"
    all_d_vec = build_sparse(all_d_content, len(all_d_content), len(all_id_to_ctg))

    print "Inverse Document Frequency"
    #all_d_vec = rebuild_distr(all_d_content)
    tfidf = build_all_idf(all_d_vec)

    print "results: " + str(len(tfidf))

    with open('tfidf_vec.csv','wb') as tfidf_out:
        writer = csv.writer(tfidf_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for idf in tfidf:
            indexes = []
            ind_cnt = 0
            for ind,d in idf,all_d_content:
                if ind > 0.0001:
                    indexes.append([ind_cnt, ind])
                ind_cnt += 1
            writer.writerow([d[0], indexes])


if __name__ == "__main__":
    main()