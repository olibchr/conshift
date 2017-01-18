
import csv
import sys
from scipy.stats import entropy
from sklearn.metrics import pairwise as pw
import string
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
path = sys.argv[2]
csv.field_size_limit(sys.maxsize)

mode = int(sys.argv[1])

distr_file = ['q1_distributions.csv','q2_distributions.csv','q3_distributions.csv','q4_distributions.csv', ]
q_char = '|'
print "MODE: Quarterly concept vectors"


def get_ctg(filters):
    filter_id_to_ctg = {}
    all_id_to_ctg = {}
    with open(path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            if int(row[1]) in filters:
                filter_id_to_ctg[int(row[1])] = row[0]
            all_id_to_ctg[int(row[1])] = row[0]
    return filter_id_to_ctg, all_id_to_ctg


def load_distr(filters):
    all_d_content = []
    allchars = ''.join(chr(i) for i in xrange(256))
    identity = string.maketrans('', '')
    nondigits = allchars.translate(identity, string.digits)
    for qtr in distr_file:
        with open(path + qtr) as distr_vec:
            reader = csv.reader(distr_vec, delimiter=',', quotechar=q_char, quoting=csv.QUOTE_MINIMAL)
            qtr_data = []
            qtr_d_content = []
            for row in reader:
                qtr_data.append(row)
            for filter in filters:
                row = qtr_data[filter]
                features = [int(k.translate(identity, nondigits)) for k in row[1].split(",")]
                l_features = [features[x] for x in range(0,len(features),2)]
                xy_features = [(k,v) for k,v in {l_features[y/2-1]:features[y] for y in range(1,len(features),2)}.items()]
                #print "     " + str(row[0]) + " --- " + str(len(xy_features))
                qtr_d_content.append([int(row[0]),xy_features])
            all_d_content.append(qtr_d_content)
            del qtr_data
    return all_d_content


def rebuild_distr(all_d_content, vlen):
    all_d_vec = []
    for d_vec in all_d_content:
        d_vector = [0.000001] * vlen
        d_id = d_vec[0]
        for keyval in d_vec[1]:
            d_vector[keyval[0]] = keyval[1]
        all_d_vec.append([d_id, d_vector])
    return all_d_vec


# might be problem: distributions might not contain a specific vector --> need identifier
def kl_div(distributions):
    if len(distributions) <2:
        print "Nothing to compare.. exiting"
        exit()
    else:
        all_div = []
        for i in range(1,len(distributions[0])):
            this_ents = []
            this_distr = distributions[0][i]
            for k in range(1,len(distributions)):
                next_distr = distributions[k][i]
                this_entropy = entropy(this_distr, next_distr)
                this_ents.append(this_entropy)
                this_distr = next_distr
            all_div.append(this_ents)
        return all_div


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
    filters = map(int, argv[3:])
    print "Setting filters.. "

    filter_id_to_ctg, all_id_to_ctg = get_ctg(filters)

    for filter in filters:
        print "     " + str(filter) + ": " + str(filter_id_to_ctg[filter].split('/')[-1])

    distributions = load_distr(filters)

    print "Create sparse vectors"
    for i in range(0,len(distributions)):
        distributions[i] = rebuild_distr(distributions[i], len(all_id_to_ctg))

    print "Built " + str(len(distributions[0])) + " probability density vectors"

    all_divergences = kl_div(distributions)

    print "KL Divergences are: "

    for d in all_divergences:
        print "     " + str(filters[0]) + " --> " + str(d[0]) + " : " + str(d[1])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: enter one or several indices from the dictionary hinting at wikipedia annotations which are preferably related. This program calculates the cosine similarity between the first entered index and all other entered indeces."
    else:
        main(sys.argv)
