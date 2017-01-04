import csv
import sys
import numpy as np
import thread
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

"""
This program calculates density distributions for all annotations and saves those as sparse vectors
"""
if len(sys.argv) < 2:
    print "Give dir path to annotion files!"
    exit()
path = sys.argv[1]

def get_ctg():
    all_id_to_ctg = {}
    with open(path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_id_to_ctg[int(row[1])] = row[0]
    return all_id_to_ctg, all_id_to_ctg


def get_items():
    all_annotations = []
    with open(path + 'annotation_vectors.csv') as annotation_vectors:
        reader = csv.reader(annotation_vectors, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for item in reader:
            annots = item[2][1:-1].split(',')
            annots = [x.strip(' ') for x in annots]
            all_annotations.append([item[0], item[1], annots])
    return sorted(all_annotations, key=lambda all_annotation: all_annotations[0])


def invert_items(all_items, filter):
    inverted_items = []
    for item in all_items:
        for annot in item[2]:
            annot = int(annot)
            inverted_items.append([annot, item])
    sorted(inverted_items, key=lambda key:inverted_items[0])
    return inverted_items


def build_vectors(inverted_items, filters, length):
    all_d_vector = []
    i = 0
    offset = 0

    for filter in filters:
        if i % 200 == 0:
            print "progress: " + str(i) + ", " + str(len(filters)) + ", " + str((i * 100) / float(1.0*len(filters))) + "%"
        i += 1
        vector = {}
        indeces = []
        for item in inverted_items[offset:]:
            offset += 1
            if item[0] == filter:
                for annot in item[1][2]:
                    if annot in vector.keys():
                        vector[annot] = vector[annot] + 1
                    else:
                        vector[annot] = 1
            else:
                break
        for k,v in vector.iteritems():
            indeces.append([k,v])
        all_d_vector.append([filter, indeces])
    return all_d_vector


def main():
    filter_id_to_ctg, all_id_to_ctg = get_ctg()

    filters = [x for x in all_id_to_ctg.keys()]

    print "Loading data.. "

    print "Annotations: " + str(len(all_id_to_ctg))

    all_items = get_items()

    print "Articles: " + str(len(all_items))

    inverted_items = invert_items(all_items, filters)

    print len(inverted_items)

    all_distributions = build_vectors(inverted_items, filters, len(all_id_to_ctg))

    with open('all_distributions.csv', 'wb') as out_file:
        writer = csv.writer(out_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for line in all_distributions:
            writer.writerow(line)


if __name__ == "__main__":
    main()
