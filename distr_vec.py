import csv
import sys
import numpy as np
import thread
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


def get_ctg():
    all_id_to_ctg = {}
    with open('annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_id_to_ctg[int(row[1])] = row[0]
    return all_id_to_ctg, all_id_to_ctg


def get_items():
    all_annotations = []
    with open('annotation_vectors.csv') as annotation_vectors:
        reader = csv.reader(annotation_vectors, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for item in reader:
            annots = item[2][1:-1].split(',')
            annots = [x.strip(' ') for x in annots]
            all_annotations.append([item[0], item[1], annots])
    return sorted(all_annotations, key=lambda all_annotation: all_annotations[0])


def filter_items(all_items, filter):
    filtered_items = []
    for item in all_items:
        for annot in item[2]:
            annot = int(annot)
            filtered_items.append([annot, item])

    return filtered_items


def write_this(dist_vec):
    with open('all_distributions.csv', 'wb') as out_file:
        writer = csv.writer(out_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for line in dist_vec:
            writer.writerow(line)


def build_vectors(filtered_items, filters, length):
    all_d_vector = []
    i = 0

    for filter in filters:
        if i % 200 == 0:
            print "progress: " + str(i) + ", " + str(len(filters)) + ", " + str((i * 100) / float(1.0*len(filters))) + "%"
        i += 1
        vector = {}
        indeces = []
        for item in filtered_items:
            if item[0] == filter:
                for annot in item[1][2]:
                    if annot in vector:
                        vector[annot] = vector[annot] + 1
                    else:
                        vector[annot] = 1
        for k,v in vector.iteritems():
            indeces.append([k,v])
        all_d_vector.append([filter, indeces])
    write_this(all_d_vector)
    return all_d_vector


def main():
    filter_id_to_ctg, all_id_to_ctg = get_ctg()

    filters = [x for x in all_id_to_ctg.keys()]

    print "Loading data.. "

    print "Annotations: " + str(len(all_id_to_ctg))

    all_items = get_items()

    print "Articles: " + str(len(all_items))

    filtered_items = filter_items(all_items, filters)

    all_distributions = build_vectors(filtered_items, filters, len(all_id_to_ctg))

    """with open('all_distributions.csv', 'wb') as all_d:
        writer = csv.writer(all_d, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for d in all_distributions:
            indexes = []
            ind_cnt = 0
            for ind in d[1]:
                if ind > 0.0001:
                    indexes.append([ind_cnt, ind])
                ind_cnt += 1
            writer.writerow([d[0], indexes])
    """


if __name__ == "__main__":
    main()
