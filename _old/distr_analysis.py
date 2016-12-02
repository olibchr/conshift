
import csv
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.stats import entropy
from sklearn.preprocessing import normalize


def get_ctg(filters):
    filter_id_to_ctg = {}
    all_id_to_ctg = {}
    with open('annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            if int(row[1]) in filters:
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
    return filtered_items


def build_vectors(filtered_items, filters, length):
    all_d_vector = []
    index_cnt = {key: 0 for key in filters}
    for filter in filters:
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


def plot_d(distributions, argv):
    print "Summed densities are: "
    i = 2
    for distr in distributions:
        distr = distr / np.sum(distr)
        print np.sum(distr)
        #density, bins = np.histogram(distr, normed=True, density=True)
        #unity_density = density / density.sum()
        plt.plot(distr)
        #fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True)
        #widths = bins[:-1] - bins[1:]
        #ax.bar(bins[1:], unity_density, width=widths)
        #plt.show()
        #plt.plot(unity_density)
        #plt.axis([0,150000,0,1])
        #plt.show()
        savename = "plots/" + str(argv[1]) + "_to_" + str(argv[i]) + ".png"
        i =+1
        plt.savefig(savename)


def kl_div(distributions):
    if len(distributions) <2:
        print "Nothing to compare.. exiting"
    else:
        all_div = []

        #gold_standard = distributions[]
        for i in range(1, len(distributions)):
            #print np.sum(distributions[0])
            #print np.sum(distributions[i])
            gold_standard = distributions[0][1]
            # print distributions[i][0]
            this_entropy = entropy(gold_standard, distributions[i][1])
            all_div.append([distributions[i][0],this_entropy])
    return all_div


def validation(distributions, all_id_to_ctg, argv):
    for i in range(1, len(distributions)):
        diff = np.subtract(np.array(distributions[0]), np.array(distributions[i]))
        # for k in range(0,len(diff)):
            # if diff[k] != 0:
                #print "Difference found in " + str(all_id_to_ctg[k])
        print "In index " + str(argv[i+1]) + " --> summed " + str(abs(np.sum(diff))) + " distance"


def main(argv):
    all_items = []
    filtered_items = []
    filter_ctg_to_id = {}
    filter_id_to_ctg = {}
    all_ctg_to_id = {}
    all_id_to_ctg = {}
    filters = [x for x in range(1,1000)]
    print "Setting filters.. "

    filter_id_to_ctg, all_id_to_ctg = get_ctg(filters)

    for filter in filters:
        print "     " + str(filter) + ": " + str(filter_id_to_ctg[filter].split('/')[-1])
    #for k,v in filter_id_to_ctg.items():
    #    print "     " + str(k) + ": " + str(v.split('/')[-1])

    print "Loading data.. "

    print "Annotations: " + str(len(all_id_to_ctg))

    all_items = get_items()

    print "Articles: " + str(len(all_items))

    filtered_items = filter_items(all_items, filters)

    distributions = build_vectors(filtered_items, filters, len(all_id_to_ctg))

    print "Built " + str(len(distributions)) + " probability density vectors"

    # plot_d(distributions, argv)

    all_divergences = kl_div(distributions)
    print "KL Divergences are: "

    for d in (all_divergences):
        print "     " + str(filters[0]) + " --> " + str(d[0]) + " : " + str(d[1])
    #for d in range(0,len(all_divergences)):
    #    print "     " + str(argv[1]) + " --> "+ str(argv[d+2]) + " : " + str(all_divergences[d])

    # validation(distributions, all_id_to_ctg,argv)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: enter one or several indices from the dictionary hinting at wikipedia annotations which are preferably related. This program calculates the cosine similarity between the first entered index and all other entered indeces."
    else:
        main(sys.argv)
