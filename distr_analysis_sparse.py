
import csv
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.stats import entropy
from sklearn.preprocessing import normalize
from sklearn.metrics import pairwise as pw
from scipy.sparse import lil_matrix
import wikipedia
import warnings
warnings.filterwarnings("ignore")

"""
The purpose of this program is to do an investigation of the data which was produced with the create vectors tool.
You have to specify one or several IDs of annotations to investigate about (ID mapping can be found in separate csv file,
produce by create vector tool as well)
In detail, this tool creates density distribution vectors for the specified annotations and compares them to each other
 with a KL divergence / cosine metric to measure similarity.
 All output will be printed on screen.
"""
path = sys.argv[1]


def get_ctg(filters):
    filter_id_to_ctg = {}
    all_id_to_ctg = {}
    with open('annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            if int(row[1]) in filters:
                filter_id_to_ctg[int(row[1])] = row[0]
            all_id_to_ctg[int(row[1])] = row[0]
    return filter_id_to_ctg, all_id_to_ctg


def load_distr(filters):
    all_d_content = []
    with open(path + 'all_distributions.csv') as distr_vec:
        reader = csv.reader(distr_vec, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        i = 0
        for row in reader:
            if i not in filters:
                i += 1
                continue
            i += 1
            features = [int(k.replace('[','').replace(']','').replace(" ","").replace("'","")) for k in row[1].split(",")]
            l_features = [features[x] for x in range(0,len(features),2)]
            xy_features = [(k,v) for k,v in {l_features[y/2-1]:features[y] for y in range(1,len(features),2)}.items()]
            all_d_content.append([int(row[0]),xy_features])
    return all_d_content


def rebuild_distr(all_d_content):
    all_d_vec = np.array()
    for d_vec in all_d_content:
        d_vector = [0.000001] * len(all_d_content)
        d_id = d_vec[0]
        for keyval in d_vec[1]:
            d_vector[keyval[0]] = keyval[1]
        all_d_vec = np.append(all_d_vec, [d_id, d_vector], axis=0)
    return all_d_vec


def kl_div(distributions):
    if len(distributions) <2:
        print "Nothing to compare.. exiting"
    else:
        all_div = []

        for i in range(1, len(distributions)):
            gold_standard = distributions[0][1]
            this_entropy = entropy(gold_standard, distributions[i][1])
            all_div.append([distributions[i][0],this_entropy])
    return all_div


def main(argv):
    filters = map(int, argv[2:])
    all_d_content = load_distr(filters)
    all_ctg_to_id, all_id_to_ctg = get_ctg(filters)
    print "Create sparse vectors"
    distributions = rebuild_distr(all_d_content)

    print "Built " + str(len(distributions)) + " probability density vectors"

    # plot_d(distributions, argv)

    all_divergences = kl_div(distributions)

    print "KL Divergences are: "

    plot_x = []
    for d in (all_divergences):
        print "     " + str(filters[0]) + " --> " + str(d[0]) + " : " + str(d[1])
        plot_x.append(d[1])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: enter one or several indices from the dictionary hinting at wikipedia annotations which are preferably related. This program calculates the cosine similarity between the first entered index and all other entered indeces."
    else:
        main(sys.argv)
