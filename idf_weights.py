import csv
import sys
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfTransformer

"""
This program computes tf-idf scores based on density vectors, created by distr_vec for all density distributions of annotations.
"""

def load_distr():
    all_d_content = []
    with open('distr_vec.csv') as distr_vec:
        reader = csv.reader(distr_vec, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_d_content.append(row)
    return all_d_content


def rebuild_distr(all_d_content):
    all_d_vec = np.array()
    for d_vec in all_d_content:
        d_vector = [0] * len(all_d_content)
        d_id = d_vec[0]
        for keyval in d_vec[1]:
            d_vector[keyval[0]] = keyval[1]
        all_d_vec = np.append(all_d_vec, [d_id, d_vector], axis=0)
    return all_d_vec


def build_all_idf(all_d_vec):
    transformer = TfidfTransformer(smooth_idf=False)
    tfidf = transformer.fit_transform(all_d_vec[:,1]).toarray()
    return transformer.idf_


def main():
    all_d_content = load_distr()
    all_d_vec = rebuild_distr(all_d_content)
    tfidf = build_all_idf(all_d_vec)

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