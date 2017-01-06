import csv
import sys, string
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from scipy.sparse import lil_matrix
import matplotlib.pyplot as plt


csv.field_size_limit(sys.maxsize)
path = sys.argv[1]
def load_distr():
    all_d_content = []
    allchars = ''.join(chr(i) for i in xrange(256))
    identity = string.maketrans('', '')
    nondigits = allchars.translate(identity, string.digits)
    with open(path + 'all_distributions.csv') as distr_vec:
        reader = csv.reader(distr_vec, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
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


def main():
    print "Loading data"
    all_d_content = load_distr()
    all_id_to_ctg = get_ctg()
    print "Create sparse vectors"
    sparse_entities = build_sparse(all_d_content, len(all_d_content), len(all_id_to_ctg))
    del all_id_to_ctg, all_d_content

    print "Clustering.."
    sparse_entities = StandardScaler(with_mean=False).fit_transform(sparse_entities)

    db = DBSCAN(eps=0.3, min_samples=10, algorithm='brute', metric='cosine').fit(all_d_content)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    print('Estimated number of clusters: %d' % n_clusters_)
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(all_d_content, labels))

    unique_labels = set(labels)
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))

    target_entities = []
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = 'k'

        class_member_mask = (labels == k)
        this_class = []
        idx = -1
        while True:
            try:
                idx = class_member_mask.tolist().index(True, idx+1)
                this_class.append(idx)
            except ValueError:
                break
        target_entities.append(this_class)

    print target_entities
    #with open(path + 'all_distr_weighted.csv', 'wb') as outfile:
    #    writer = csv.writer(outfile, delimiter=',', quotechar='|',quoting=csv.QUOTE_MINIMAL)
    #    for line in target_entities:
    #        writer.writerow(line)


if __name__ == "__main__":
    main()