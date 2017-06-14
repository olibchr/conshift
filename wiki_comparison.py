from concept_time_analysis import Concept, get_ctg, load_doc_map, load_idf_weights, load_distr
import sys, csv
import warnings
import datetime
import random
from sklearn.preprocessing import normalize
from sklearn.metrics import pairwise as pw
import math, json, io
import scipy
warnings.filterwarnings("ignore")
csv.field_size_limit(sys.maxsize)
sys.path.append('7_wikiedits/')
from edit_retrieval import WikiEdits

# Init global vars
concepts = []
filter_id_to_ctg, all_id_to_ctg, all_ctg_to_id, docid_to_date, weights = {}, {}, {}, {}, {}
DATEONE = datetime.datetime.strptime("2014-08-14", "%Y-%m-%d")
DATELAST = datetime.datetime.strptime("2015-08-14", "%Y-%m-%d")


def filter_selector(requested):
    id_to_cnt = []
    with open('offset_communicator','r+') as offsetfile:
        off = offsetfile.read()
        if off == '': offsetfile.write(str(requested)); off = 0
        else: offsetfile.write(str(int(off)+requested)); off = int(off)

    with open('index_cnt.csv', 'r') as in_file:
        reader = csv.reader(in_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for line in reader:
            id_to_cnt.append([int(line[1]), int(line[2])])
    offset1 = int(off)
    offset2 = int(off)
    for item in id_to_cnt:
        if item[1] > 1000: offset1 +=1 # tbd
        if item[1] > 10: offset2 += 1 # tbd
        else: break
    if off > offset1-off:
        return [e[0] for e in id_to_cnt[offset1:requested+offset1]] + [e[0] for e in id_to_cnt[offset2:requested+offset2]]
    if off > offset2-off:
        return [e[0] for e in id_to_cnt[offset2:requested+offset2]]
    return [e[0] for e in id_to_cnt[:requested]] + [e[0] for e in id_to_cnt[offset1:requested+offset1]] + [e[0] for e in id_to_cnt[offset2:requested+offset2]]


def comparator(concepts_cosines, wikiedit_counts):
    print concepts_cosines, wikiedit_counts
    corr, r_val = scipy.stats.spearmanr(concepts_cosines, wikiedit_counts)
    return corr, r_val


# Experiment 1 - Test fix vector size
def experiment_1(filters, path):
    print "Experiment 1"
    pref = 'all'
    global filter_id_to_ctg, all_id_to_ctg, all_ctg_to_id, concepts, docid_to_date, weights
    filter_id_to_ctg, all_id_to_ctg = get_ctg(path, filters)
    print filters
    all_ctg_to_id = {v:k for k,v in all_id_to_ctg.iteritems()}
    docid_to_date = load_doc_map(path)
    weights = load_idf_weights(path)
    concepts = load_distr(path, pref, filters, filter_id_to_ctg)
    print "Building Concepts"
    for con in concepts:
        try:
            con.into_fixed_timeframes(docid_to_date)
            con.rebuild_fix_dist(weights, all_id_to_ctg)
            con.get_cosim(vector="fix")
            #con.print_cosim()
            print "     " + con.name + " built successfully"
        except Exception:
            print "Fatal error with concept"
            concepts.pop(concepts.index(con))
    print "Getting edits of " + str(len(concepts)) + " concepts"
    wikiedits = []
    now = str(datetime.datetime.now().date())
    out_results = []
    for con in concepts:
        try:
            wkedit = WikiEdits(data_dir='7_wikiedits/wikijson')
            wikiedits.append(wkedit)
            wkedit.parse(con.name)
            wkedit.split_revisions(con.fixIntervals)
            if len(wkedit.rev_tf_sums) == 0: continue
            spear, p_val = comparator(con.cosim, wkedit.rev_tf_sums)
            result = {
                'concept': con.name,
                'id': con.id,
                'intervals': [str(dt.date()) for dt in con.fixIntervals],
                'cosines': con.cosim,
                'wkedits': wkedit.rev_tf_sums,
                'spearman': spear,
                'p': p_val
            }
            out_results.append(result)
            print "     " + str(spear) + " spearman corr of concept " + con.name + " with p " + str(p_val)
            del wkedit
        except Exception:
            print 'Fatal Error with wiki edits'
        del con
    outfile = '8_experiments/results_exp1_' + now + '.json'
    print('Writing results to {}').format(outfile)
    with io.open(outfile, 'a', encoding='utf-8') as f:
        f.write(unicode(json.dumps(out_results, encoding='utf8', ensure_ascii=False)+ '\n'))


# Experiment 2 - Test flexible vector size
def experiment_2(filters, path):
    print "Experiment 2"
    pref = 'all'
    global filter_id_to_ctg, all_id_to_ctg, all_ctg_to_id, concepts, docid_to_date, weights
    filter_id_to_ctg, all_id_to_ctg = get_ctg(path, filters)
    print filters
    all_ctg_to_id = {v:k for k,v in all_id_to_ctg.iteritems()}
    docid_to_date = load_doc_map(path)
    weights = load_idf_weights(path)
    concepts = load_distr(path, pref, filters, filter_id_to_ctg)
    print "Building Concepts"
    for con in concepts:
        try:
            #if len(set(item.split('_')[1] for item in con.features)) < 4: concepts.pop(concepts.index(con)); print "too few articles in " + con.name; continue
            print "splitting in intervals"
            print len(set(item.split('_')[1] for item in con.features)), math.floor(len(set(item.split('_')[1] for item in con.features))/12.0)
            bucketsize = math.floor(len(set(item.split('_')[1] for item in con.features))/12.0)
            con.into_flex_timeframes(docid_to_date, bucketsize)
            con.rebuild_flex_dist(weights, all_id_to_ctg)
            con.get_cosim()
            #con.print_cosim()
            print "     " + con.name + " built successfully"
        except Exception:
            print "Fatal error with concept"
            concepts.pop(concepts.index(con))
    print "Getting edits of " + str(len(concepts)) + " concepts"
    wikiedits = []
    now = str(datetime.datetime.now().date())
    out_results = []
    for con in concepts:
        try:
            wkedit = WikiEdits(data_dir='7_wikiedits/wikijson')
            wikiedits.append(wkedit)
            wkedit.parse(con.name)
            wkedit.split_revisions(con.flexIntervals)
            if len(wkedit.rev_tf_sums) == 0: continue
            spear, p_val = comparator(con.cosim, wkedit.rev_tf_sums)
            result = {
                'concept': con.name,
                'id': con.id,
                'intervals': [str(dt.date()) for dt in con.flexIntervals],
                'cosines': con.cosim,
                'wkedits': wkedit.rev_tf_sums,
                'spearman': spear,
                'p': p_val
            }
            out_results.append(result)
            print "     " + str(spear) + " spearman corr of concept " + con.name + " with p " + str(p_val)
            del wkedit
        except Exception:
            print 'Fatal Error with wiki edits'
        del con
    outfile = '8_experiments/results_exp2_' + now + '.json'
    print('Writing results to {}').format(outfile)
    with io.open(outfile, 'a', encoding='utf-8') as f:
        f.write(unicode(json.dumps(out_results, encoding='utf8', ensure_ascii=False)+ '\n'))


# Experiment 3 - Test no idf weighting
def experiment_3():
    print "Experiment 3"
    path = '/Users/oliverbecher/1_data/0_cwi/1_data/'
    #path = '/export/scratch1/home/becher/data/'
    pref = 'all'
    filters = random.sample(xrange(71564), 100)
    global filter_id_to_ctg, all_id_to_ctg, all_ctg_to_id, concepts, docid_to_date, weights
    filter_id_to_ctg, all_id_to_ctg = get_ctg(path, filters)
    print filters
    all_ctg_to_id = {v:k for k,v in all_id_to_ctg.iteritems()}
    docid_to_date = load_doc_map(path)
    weights = load_idf_weights(path)
    concepts = load_distr(path, pref, filters, filter_id_to_ctg)
    print "Building Concepts"
    for con in concepts:
        if len(set(item.split('_')[1] for item in con.features)) < 4: concepts.pop(concepts.index(con)); print "too few articles in " + con.name; continue
        print "splitting in intervals"
        print len(set(item.split('_')[1] for item in con.features)), math.floor(len(set(item.split('_')[1] for item in con.features))/4.0)
        con.into_flex_timeframes(docid_to_date, math.floor(len(set(item.split('_')[1] for item in con.features))/4.0))
        con.rebuild_flex_dist(weights, all_id_to_ctg, weightsON=False)
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


# Experiment 4 - Test one publisher at a time vs wikipedia
def experiment_4():
    print "Experiment 4"
    path = '/Users/oliverbecher/1_data/0_cwi/1_data/'
    #path = '/export/scratch1/home/becher/data/'
    splitsize = 4.0

    pref = 'DM'
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
        if len(set(item.split('_')[1] for item in con.features)) < 4: concepts.pop(concepts.index(con)); print "too few articles in " + con.name; continue
        print "splitting in intervals"
        print len(set(item.split('_')[1] for item in con.features)), math.floor(len(set(item.split('_')[1] for item in con.features))/splitsize)
        con.into_flex_timeframes(docid_to_date, math.floor(len(set(item.split('_')[1] for item in con.features))/splitsize))
        con.rebuild_flex_dist(weights, all_id_to_ctg)
        con.get_cosim()
        con.print_cosim()
        print "     " + con.name + " built successfully"
    print "Getting edits of " + str(len(concepts)) + " concepts"
    wikiedits = []
    results = dict()
    now = str(datetime.datetime.now().date())
    for con in concepts:
        f = open('8_experiments/results_exp3' + now + pref + '.csv', 'a')
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

    pref = 'HP'
    concepts = load_distr(path, pref, filters, filter_id_to_ctg)
    print "Building Concepts"
    for con in concepts:
        if len(set(item.split('_')[1] for item in con.features)) < 4: concepts.pop(concepts.index(con)); print "too few articles in " + con.name; continue
        print "splitting in intervals"
        print len(set(item.split('_')[1] for item in con.features)), math.floor(len(set(item.split('_')[1] for item in con.features))/splitsize)
        con.into_flex_timeframes(docid_to_date, math.floor(len(set(item.split('_')[1] for item in con.features))/splitsize))
        con.rebuild_flex_dist(weights, all_id_to_ctg)
        con.get_cosim()
        con.print_cosim()
        print "     " + con.name + " built successfully"
    print "Getting edits of " + str(len(concepts)) + " concepts"
    wikiedits = []
    results = dict()
    now = str(datetime.datetime.now().date())
    for con in concepts:
        f = open('8_experiments/results_exp3' + now + pref + '.csv', 'a')
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

    pref = 'IND'
    concepts = load_distr(path, pref, filters, filter_id_to_ctg)
    print "Building Concepts"
    for con in concepts:
        if len(set(item.split('_')[1] for item in con.features)) < 4: concepts.pop(concepts.index(con)); print "too few articles in " + con.name; continue
        print "splitting in intervals"
        print len(set(item.split('_')[1] for item in con.features)), math.floor(len(set(item.split('_')[1] for item in con.features))/splitsize)
        con.into_flex_timeframes(docid_to_date, math.floor(len(set(item.split('_')[1] for item in con.features))/splitsize))
        con.rebuild_flex_dist(weights, all_id_to_ctg)
        con.get_cosim()
        con.print_cosim()
        print "     " + con.name + " built successfully"
    print "Getting edits of " + str(len(concepts)) + " concepts"
    wikiedits = []
    results = dict()
    now = str(datetime.datetime.now().date())
    for con in concepts:
        f = open('8_experiments/results_exp3' + now + pref + '.csv', 'a')
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

    pref = 'NYT'
    concepts = load_distr(path, pref, filters, filter_id_to_ctg)
    print "Building Concepts"
    for con in concepts:
        if len(set(item.split('_')[1] for item in con.features)) < 4: concepts.pop(concepts.index(con)); print "too few articles in " + con.name; continue
        print "splitting in intervals"
        print len(set(item.split('_')[1] for item in con.features)), math.floor(len(set(item.split('_')[1] for item in con.features))/splitsize)
        con.into_flex_timeframes(docid_to_date, math.floor(len(set(item.split('_')[1] for item in con.features))/splitsize))
        con.rebuild_flex_dist(weights, all_id_to_ctg)
        con.get_cosim()
        con.print_cosim()
        print "     " + con.name + " built successfully"
    print "Getting edits of " + str(len(concepts)) + " concepts"
    wikiedits = []
    results = dict()
    now = str(datetime.datetime.now().date())
    for con in concepts:
        f = open('8_experiments/results_exp3' + now + pref + '.csv', 'a')
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

    pref = 'WP'
    concepts = load_distr(path, pref, filters, filter_id_to_ctg)
    print "Building Concepts"
    for con in concepts:
        if len(set(item.split('_')[1] for item in con.features)) < 4: concepts.pop(concepts.index(con)); print "too few articles in " + con.name; continue
        print "splitting in intervals"
        print len(set(item.split('_')[1] for item in con.features)), math.floor(len(set(item.split('_')[1] for item in con.features))/splitsize)
        con.into_flex_timeframes(docid_to_date, math.floor(len(set(item.split('_')[1] for item in con.features))/splitsize))
        con.rebuild_flex_dist(weights, all_id_to_ctg)
        con.get_cosim()
        con.print_cosim()
        print "     " + con.name + " built successfully"
    print "Getting edits of " + str(len(concepts)) + " concepts"
    wikiedits = []
    results = dict()
    now = str(datetime.datetime.now().date())
    for con in concepts:
        f = open('8_experiments/results_exp3' + now + pref + '.csv', 'a')
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

if __name__ == "__main__":
    experiment_1(random.sample(xrange(71564), 6))