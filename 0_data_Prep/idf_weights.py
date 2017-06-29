import csv
import sys
import numpy as np
import pandas as pd
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


def load_distr():
    all_d_content = []
    with open(path + 'all_distributions_time.csv') as distr_vec:
        reader = csv.reader(distr_vec, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            features = {}
            thisCon = row[1:]
            for feat in thisCon:
                feat = feat.split("_")[0]
                if feat in features:
                    features[int(feat)] += 1
                else: features[int(feat)] = 1
            all_d_content.append([int(row[0]), [[k,v] for k,v in features.iteritems()]])
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


def build_all_idf(all_d_vec, all_d_content):
    transformer = TfidfTransformer(smooth_idf=False)
    sparse_entities = transformer.fit_transform(all_d_vec)
    idf = transformer.idf_
    print "Weigths"
    weights = np.asarray(sparse_entities.mean(axis=0)).ravel().tolist()
    weights_df = pd.DataFrame({'term': [i[0] for i in all_d_content], 'weight': weights})
    weights_df.sort_values(by='weight', ascending=False).head(20)
    print weights_df
    return dict(zip([i[0] for i in all_d_content], idf))


def main():
    all_d_content = load_distr()
    all_id_to_ctg = get_ctg()
    print "Create sparse vectors"
    sparse_entities = build_sparse(all_d_content, len(all_d_content), len(all_id_to_ctg))
    print "Inverse Document Frequency"
    weights_sparse_entities = build_all_idf(sparse_entities, all_d_content)

    with open(path + "all_distributions_weights_upd.csv", 'wb') as outfile:
        writer = csv.writer(outfile, delimiter=',', quotechar='|',quoting=csv.QUOTE_MINIMAL)
        for key, value in weights_sparse_entities.items():
            writer.writerow([key, value])


if __name__ == "__main__":
    main()