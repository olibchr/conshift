import csv
import sys
import numpy as np
import pickle, string
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfTransformer
from scipy.sparse import lil_matrix
from sklearn.preprocessing import normalize

"""
This program computes tf-idf scores based on density vectors, created by distr_vec for all density distributions of annotations.
"""
csv.field_size_limit(sys.maxsize)
path = sys.argv[1]
outfilename = 'all_distr_weighted.csv'


def load_distr():
    all_d_content = []
    allchars = ''.join(chr(i) for i in xrange(256))
    identity = string.maketrans('', '')
    nondigits = allchars.translate(identity, string.digits)
    with open(path + 'all_distributions.csv') as distr_vec:
        reader = csv.reader(distr_vec, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            features = [int(k.translate(identity, nondigits)) for k in row[1].split(",")]
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
    return all_id_to_ctg


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

    #if dim_red == '1':
    #global outfilename
    #print "Reducing Dimensionality"
    #svd = TruncatedSVD(n_components=10000, n_iter=7)
    #svd.fit(sparse_entities)
    #outfilename = 'all_distr_weighted_svd.csv'
    #return svd.components_

    return normalize(sparse_entities, norm='l1', axis=1)


def revert(sparse_entities):
    all_distributions = []
    sparse_entities = sparse_entities.tolil()
    for i in range(0,sparse_entities.shape[0]):
        this_row = sparse_entities.getrow(i)
        this_features = []
        for offset in range(0,len(this_row.data[0])):
            this_features.append((this_row.rows[0][offset], this_row.data[0][offset]))
        all_distributions.append((i,this_features))
    return all_distributions


def main():
    all_d_content = load_distr()
    all_id_to_ctg = get_ctg()
    print "Create sparse vectors"
    sparse_entities = build_sparse(all_d_content, len(all_d_content), len(all_id_to_ctg))
    del all_id_to_ctg, all_d_content
    print "Inverse Document Frequency"
    sparse_entities = build_all_idf(sparse_entities)

    all_distributions = revert(sparse_entities)
    del sparse_entities

    with open(path + outfilename, 'wb') as outfile:
        writer = csv.writer(outfile, delimiter=',', quotechar='|',quoting=csv.QUOTE_MINIMAL)
        for line in all_distributions:
            writer.writerow(line)


if __name__ == "__main__":
    main()