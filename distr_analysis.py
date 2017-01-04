
import csv
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.stats import entropy
from sklearn.preprocessing import normalize
from sklearn.metrics import pairwise as pw
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
    return filtered_items, index_cnt


"""
def rel_links(link, id_ctg):
    link = str(link.split('/')[-1]).replace("_", " ").replace("Category:", "")
    try:
        this_page = wikipedia.page(title=link)
        assc_links = this_page.section('See also')
    except Exception:
        return []
    if assc_links == None:
        return []
    assc_links = assc_links.split('\n')
    # print "Got " + str(len(assc_links))  + " links."
    result_ids = []
    for assc in assc_links:
        try:
            this_assc = wikipedia.page(title=assc)
        except Exception:
            continue
        scrapurl = "http://en.wikipedia.org/wiki/" + str((this_assc.url).split('/')[-1])
        if scrapurl in id_ctg:
            result_ids.append(id_ctg[scrapurl])
    # print "returning " + str(len(result_ids)) + " links."
    return result_ids


def get_link_annotations(filtered_items, all_id_to_ctg):
    inv_map = {v: k for k, v in all_id_to_ctg.iteritems()}
    id_ctg = [[k, v] for k, v in all_id_to_ctg.iteritems()]
    improvement_cnt = 0
    for item in filtered_items:
        #print item
        # get wikipedia related section and parse links into list
        related_ids = rel_links(all_id_to_ctg[int(item[0])], inv_map)
        if len(related_ids) == 0:
            # print "empty return"
            continue

        for rel_link in related_ids:
            if rel_link in item[1][2]:
                continue
            if rel_link in all_id_to_ctg:
                item[1][2].append(rel_link)
                # print 'done!'
                improvement_cnt += 1
                continue
        #print item
    print "Added " + str(improvement_cnt) + " annotations from wikipedia 'see also' section."
    return filtered_items
"""


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
        plt.plot(distr)
        savename = "plots/" + str(argv[1]) + "_to_" + str(argv[i]) + ".png"
        i =+1
        plt.savefig(savename)


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


def c_sim(distributions):
    if len(distributions) <2:
        print "Nothing to compare.. exiting"
    else:
        all_sim = []

        for i in range(1, len(distributions)):
            gold_standard = distributions[0][1]
            this_sim = pw.cosine_similarity(gold_standard, distributions[i][1])
            all_sim.append([distributions[i][0],this_sim])
    return all_sim


def validation(distributions, all_id_to_ctg, argv):
    for i in range(1, len(distributions)):
        diff = np.subtract(np.array(distributions[0]), np.array(distributions[i]))
        # for k in range(0,len(diff)):
            # if diff[k] != 0:
                #print "Difference found in " + str(all_id_to_ctg[k])
        print "In index " + str(argv[i+1]) + " --> summed " + str(abs(np.sum(diff))) + " distance"


def validation_scoring(distributions):
    scoring = [0] * len(distributions)
    gold_standard = distributions[0]
    k = 0
    for d in distributions:
        for i in range(0,len(d[1])):
            if (d[1][i] >= 0.00001) and (gold_standard[1][i] >= 0.00001):
                scoring[k] += 1
        k += 1
    return scoring


def main(argv):
    all_items = []
    filtered_items = []
    filter_ctg_to_id = {}
    filter_id_to_ctg = {}
    all_ctg_to_id = {}
    all_id_to_ctg = {}
    filters = map(int,argv[1:])
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

    filtered_items, article_cnt = filter_items(all_items, filters)

    distributions = build_vectors(filtered_items, filters, len(all_id_to_ctg))

    print "Built " + str(len(distributions)) + " probability density vectors"

    # plot_d(distributions, argv)

    all_divergences = kl_div(distributions)
    print "KL Divergences are: "

    plot_x = []
    for d in (all_divergences):
        print "     " + str(filters[0]) + " --> " + str(d[0]) + " : " + str(d[1])
        plot_x.append(d[1])

    all_similarities = c_sim(distributions)
    print "Cosine Similarities are: "
    for d in (all_similarities):
        print "     " + str(filters[0]) + " --> " + str(d[0]) + " : " + str(d[1])


    scoring = validation_scoring(distributions)

    print "Overlapping indices: "
    k = 0
    for score in scoring:
        print "     " + str(filters[0]) + " --> " + str(filters[k]) + " : " + str(score) + " hits."
        k += 1

    plt.plot(article_cnt.values()[1:], plot_x, 'rx')
    #plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: enter one or several indices from the dictionary hinting at wikipedia annotations which are preferably related. This program calculates the cosine similarity between the first entered index and all other entered indeces."
    else:
        main(sys.argv)
