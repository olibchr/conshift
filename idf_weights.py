import csv
import sys
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfTransformer


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
    index_cnt = {key: 0 for key in filter}
    filtered_items = []
    for item in all_items:
        for annot in item[2]:
            annot = int(annot)
            if annot in filter:
                filtered_items.append([annot, item])
                index_cnt[annot] = index_cnt[annot] + 1
    for key in filter:
        print "     " + str(key) + ": " + str(index_cnt[key]) + " articles."
    print "Loaded in total " + str(sum(val for val in index_cnt.values())) + " articles."
    return filtered_items, index_cnt


def build_vectors(filtered_items, filters, length):
    all_d_vector = []
    index_cnt = {key: 0 for key in filters}
    i = 0
    for filter in filters:
        if i % 500 == 0:
            print "Progress: " + str(i/len(filters))
        vector = []
        for item in filtered_items:
            if item[0] == filter:
                this_vector = [0.000001] * length
                for annot in item[1][2]:
                    #print annot
                    this_vector[int(annot)] = 1
                    index_cnt[filter] = index_cnt[filter] +1

                vector.append(this_vector)
        # vector = normalize(vector)
        vector = np.average(vector, axis=0)
        all_d_vector.append([filter, vector])

    # just for printing
    i = 0
    for vec in all_d_vector:
        print "     " + str(filters[i]) + ": " + str(int(sum(vec[1]))) + " annotations."
        i += 1
    return all_d_vector


def build_all_idf(distributions):
    transformer = TfidfTransformer(smooth_idf=False)
    tfidf = transformer.fit_transform(distributions[:][1]).toarray()
    return transformer.idf_


def main():
    filter_id_to_ctg, all_id_to_ctg = get_ctg()

    filters = [x for x in all_id_to_ctg.keys()]

    print "Loading data.. "

    print "Annotations: " + str(len(all_id_to_ctg))

    all_items = get_items()

    print "Articles: " + str(len(all_items))

    filtered_items, article_cnt = filter_items(all_items, filters)

    print "Building vectors.."

    distributions = build_vectors(filtered_items, filters, len(all_id_to_ctg))

    tfidf = build_all_idf(distributions)

    with open('tf-idf_weights.csv', 'wb') as article_vec_out:
        writer = csv.writer(article_vec_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for t in tfidf:
            writer.writerow(t)


if __name__ == "__main__":
    main()