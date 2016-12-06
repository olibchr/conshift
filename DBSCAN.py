import csv
import sys
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler


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


def dbscan(all_d_content):
    all_d_content = StandardScaler().fit_transform(all_d_content)
    db = DBSCAN(eps=0.3, min_samples=10).fit(all_d_content)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    print('Estimated number of clusters: %d' % n_clusters_)
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(all_d_content, labels))