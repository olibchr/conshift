
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
    index_cnt = {key: 0 for key in filter_id_to_ctg.keys()}
    filtered_items = []
    for item in all_items:
        for annot in item[2]:
            annot = int(annot)
            if annot in filter_id_to_ctg:
                filtered_items.append([annot, item])
                index_cnt[annot] = index_cnt[annot] + 1
    print index_cnt
    print str(sum(val for val in index_cnt.values()))
    return filtered_items


def build_vectors(filtered_items, filter_id_to_ctg, length):
    all_d_vector = []
    index_cnt = {key: 0 for key in filter_id_to_ctg.keys()}
    for filter in filter_id_to_ctg.keys():
        vector = []
        for item in filtered_items:
            if item[0] == filter:
                this_vector = [0.000001] * length
                for annot in item[1][2]:
                    #print annot
                    this_vector[int(annot)] = 1
                    index_cnt[filter] = index_cnt[filter] +1

                vector.append(this_vector)
        vector = np.average(vector, axis=0)
        all_d_vector.append(vector)
    #print len(all_d_vector)
    print index_cnt
    for vec in all_d_vector:
        print "Vector sum is: " + str(sum(vec))

    all_d_vector = normalize(all_d_vector)
    #all_d_vector = np.reshape(all_d_vector, (1, length))
    #print all_d_vector.shape
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
        for i in range(1, len(distributions)):
            #print np.sum(distributions[0])
            #print np.sum(distributions[i])
            this_entropy = entropy(distributions[0], distributions[i])
            all_div.append(this_entropy)
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
    filters = set(argv)
    print "Setting filters.. "

    filter_id_to_ctg, all_id_to_ctg = get_ctg(filters)

    for k,v in filter_id_to_ctg.items():
        print str(k) + ": " + str(v)

    print "Loading data.. "

    print "Annotations: " + str(len(all_id_to_ctg))

    all_items = get_items()

    print "Articles: " + str(len(all_items))

    filtered_items = filter_items(all_items, filter_id_to_ctg)

    for filter in filter_id_to_ctg.values():
        print "Articles with specified annotation: " + filter + " gave " + str(sum(1 for x in (lambda x: x==filter for x in filtered_items))) + " results."

    distributions = build_vectors(filtered_items, filter_id_to_ctg, len(all_id_to_ctg))

    print "Built " + str(len(distributions)) + " probability density vectors"

    plot_d(distributions, argv)
    all_divergences = kl_div(distributions)
    print "KL Divergences towards " + str(argv[1]) + " are: "

    for d in range(0,len(all_divergences)):
        print "Index: " + str(argv[d+2]) + " --> " + str(all_divergences[d])

    validation(distributions, all_id_to_ctg,argv)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: enter one or several indices from the dictionary hinting at wikipedia annotations which are preferably related. This program calculates the cosine similarity between the first entered index and all other entered indeces."
    else:
        main(sys.argv)
