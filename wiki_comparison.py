from concept_time_analysis import Concept, get_ctg, load_doc_map, load_idf_weights, load_distr
import sys, csv
import warnings
import datetime
import random
from sklearn.preprocessing import normalize
from sklearn.metrics import pairwise as pw
import math
warnings.filterwarnings("ignore")
csv.field_size_limit(sys.maxsize)
sys.path.append('7_wikiedits/')
from edit_retrieval import WikiEdits

# Init global vars
concepts = []
filter_id_to_ctg, all_id_to_ctg, all_ctg_to_id, docid_to_date, weights = {}, {}, {}, {}, {}
DATEONE = datetime.datetime.strptime("2014-08-14", "%Y-%m-%d")
DATELAST = datetime.datetime.strptime("2015-08-14", "%Y-%m-%d")

def comparator(concepts_cosines, wikiedit_counts):
    wkedits = normalize(wikiedit_counts)
    wkedits = [1-e for e in wkedits]
    return pw.cosine_similarity(concepts_cosines, wkedits)[0][0]

# Experiment 1 - Test fix vector size
def experiment_1():
    print "Experiment 1"
    path = '/export/scratch1/home/becher/data/'
    #path = '/Users/oliverbecher/1_data/0_cwi/1_data/'
    pref = 'all'
    bucketsize = 0
    filters = random.sample(xrange(71564), 50)
    global filter_id_to_ctg, all_id_to_ctg, all_ctg_to_id, concepts, docid_to_date, weights
    filter_id_to_ctg, all_id_to_ctg = get_ctg(path, filters)
    print filters
    all_ctg_to_id = {v:k for k,v in all_id_to_ctg.iteritems()}
    docid_to_date = load_doc_map(path)
    weights = load_idf_weights(path)
    concepts = load_distr(path, pref, filters, filter_id_to_ctg)
    print "Building Concepts"
    for con in concepts:
        #if len(set(item.split('_')[1] for item in con.features)) < 12: concepts.pop(concepts.index(con)); continue
        con.into_fixed_timeframes(docid_to_date)
        con.rebuild_fix_dist(weights, all_id_to_ctg)
        con.get_cosim(vector="fix")
        #con.print_cosim()
        print "     " + con.name + " built successfully"
    print "Getting edits of " + str(len(concepts)) + " concepts"
    wikiedits = []
    results = dict()
    now = str(datetime.datetime.now().date())
    for con in concepts:
        f = open('8_experiments/results_exp1_' + now + '.csv', 'a')
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        wkedit = WikiEdits(data_dir='7_wikiedits/wikixml')
        wikiedits.append(wkedit)
        wkedit.parse(con.name)
        wkedit.split_revisions(con.fixIntervals)
        if len(wkedit.rev_tf_sums) == 0: continue
        match = comparator(con.cosim, wkedit.rev_tf_sums)
        results[con.name] = match
        print "     " + str(match) + " cosine match of concept " + con.name
        writer.writerow([con.name, con.id, results[con.name]])
        f.close()
        del wkedit
        del con
        #writer.writerow(['Average Cosine', sum([k for k in results.itervalues()])/len(results)])
#experiment_1()


# Experiment 2 - Test flexible vector size
def experiment_2():
    print "Experiment 2"
    path = '/export/scratch1/home/becher/data/'
    pref = 'all'
    bucketsize = 0
    filters = random.sample(xrange(71564), 10)
    global filter_id_to_ctg, all_id_to_ctg, all_ctg_to_id, concepts, docid_to_date, weights
    filter_id_to_ctg, all_id_to_ctg = get_ctg(path, filters)
    print filters
    all_ctg_to_id = {v:k for k,v in all_id_to_ctg.iteritems()}
    docid_to_date = load_doc_map(path)
    weights = load_idf_weights(path)
    concepts = load_distr(path, pref, filters, filter_id_to_ctg)
    print "Building Concepts"
    for con in concepts:
        #if len(set(item.split('_')[1] for item in con.features)) < 12: concepts.pop(concepts.index(con)); continue
        print "splitting in intervals"
        print len(set(item.split('_')[1] for item in con.features)), math.floor(len(set(item.split('_')[1] for item in con.features))/2.0)
        con.into_flex_timeframes(docid_to_date, math.floor(len(set(item.split('_')[1] for item in con.features))/2.0))
        con.rebuild_flex_dist(weights, all_id_to_ctg)
        con.get_cosim()
        con.print_cosim()
        print "     " + con.name + " built successfully"
    print "Getting edits of " + str(len(concepts)) + " concepts"
    wikiedits = []
    results = dict()
    now = str(datetime.datetime.now().date())
    for con in concepts:
        f = open('8_experiments/results_exp2' + now + '.csv', 'a')
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        wkedit = WikiEdits(data_dir='7_wikiedits/wikixml')
        wikiedits.append(wkedit)
        wkedit.parse(con.name)
        wkedit.split_revisions(con.flexIntervals)
        if len(wkedit.rev_tf_sums) == 0: continue
        match = comparator(con.cosim, wkedit.rev_tf_sums)
        results[con.name] = match
        print "     " + str(match) + " cosine match of concept " + con.name
        writer.writerow([con.name, con.id, results[con.name]])
        f.close()
        del wkedit
        del con
        #writer.writerow(['Average Cosine', sum([k for k in results.itervalues()])/len(results)])
experiment_2()