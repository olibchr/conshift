
import csv
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


def get_ctg(filters):
    filter_id_to_ctg = {}
    all_id_to_ctg = {}
    with open('annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            if row[1] in filters:
                # filter_ctg_to_id[row[0]] = int(row[1])
                filter_id_to_ctg[int(row[1])] = row[0]
            all_id_to_ctg[int(row[1])] = row[0]
    return filter_id_to_ctg, all_id_to_ctg


def get_items():
    all_annotations = []
    with open('annotation_vectors.csv') as annotation_vectors:
        reader = csv.reader(annotation_vectors, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for item in reader:
            annots = item[2][1:-1].split(',')
            annots = [x.strip(' ') for x in annots]
            all_annotations.append([item[0], item[1], annots])
    return sorted(all_annotations, key=lambda all_annotation: all_annotations[0])


def filter_items(all_items, filter_id_to_ctg):
    filtered_items = []
    for item in all_items:
        for annot in item[2]:
            annot = int(annot)
            if annot in filter_id_to_ctg:
                filtered_items.append([annot, item])
    return filtered_items

def build_vectors(filtered_items, filter_id_to_ctg, length):
    all_d_vector = []
    for filter in filter_id_to_ctg.keys():
        vector = []
        for item in filtered_items:
            if item[0] == filter:
                this_vector = [0] * length
                for annot in item[1][2]:
                    #print annot
                    this_vector[int(annot)] = 1
                vector.append(this_vector)
        vector = np.average(vector, axis=0)

        all_d_vector.append(vector)
    print len(all_d_vector)
    #all_d_vector = np.reshape(all_d_vector, (1, length))
    #print all_d_vector.shape
    return all_d_vector


def plot_d(distributions):
    for distr in distributions:
        density, bins = np.histogram(distr, normed=True, density=True)
        unity_density = density / density.sum()
        fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True)
        widths = bins[:-1] - bins[1:]
        ax.bar(bins[1:], unity_density, width=widths)
        plt.show()
        #plt.plot(unity_density)
        #plt.axis([0,150000,0,1])
        #plt.show()


def main(argv):
    all_items = []
    filtered_items = []
    filter_ctg_to_id = {}
    filter_id_to_ctg = {}
    all_ctg_to_id = {}
    all_id_to_ctg = {}
    filters = set(argv)

    filter_id_to_ctg, all_id_to_ctg = get_ctg(filters)

    print filter_id_to_ctg
    print "Annotations: " + str(len(all_id_to_ctg))

    all_items = get_items()

    print "Articles: " + str(len(all_items))

    filtered_items = filter_items(all_items, filter_id_to_ctg)

    print "Articles with specified annotation: " + str(len(filtered_items))

    distributions = build_vectors(filtered_items, filter_id_to_ctg, len(all_id_to_ctg))

    print "Built " + str(len(distributions)) + " distribution vectors"

    plot_d(distributions)


if __name__ == "__main__":
    main(sys.argv)
