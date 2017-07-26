from concept_time_analysis import get_ctg, load_doc_map, load_idf_weights, load_distr
import sys, csv
import warnings
import datetime
import random
from sklearn.preprocessing import normalize
from sklearn.metrics import pairwise as pw
import math, json, io
import scipy.stats
warnings.filterwarnings("ignore")
csv.field_size_limit(sys.maxsize)
sys.path.append('4_wikiedits/')
from edit_retrieval import WikiEdits

# Init global vars
concepts = []
filter_id_to_ctg, all_id_to_ctg, all_ctg_to_id, docid_to_date, weights = {}, {}, {}, {}, {}
DATEONE = datetime.datetime.strptime("2014-08-14", "%Y-%m-%d")
DATELAST = datetime.datetime.strptime("2015-08-14", "%Y-%m-%d")


def comparator(concepts_cosines, wikiedit_counts):
    #print concepts_cosines, wikiedit_counts
    corr, r_val = scipy.stats.spearmanr(concepts_cosines, wikiedit_counts)
    return corr, r_val


# Experiment 1 - Test fix vector size
def experiment_1(filters, path, vsize):
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
            con.into_fixed_timeframes(docid_to_date, vsize)
            con.rebuild_fix_dist(weights, all_id_to_ctg)
            con.get_cosim(vector="fix")
            #con.print_cosim()
            print "     " + con.name + " built successfully"
        except Exception as e:
            print "Fatal error with concept: " + con.name + ", " + str(con.id) + "; Reason: "+ str(e)
            concepts.pop(concepts.index(con))
    print "Getting edits of " + str(len(concepts)) + " concepts"
    wikiedits = []
    now = str(datetime.datetime.now().date())
    out_results = []
    for con in concepts:
        try:
            wkedit = WikiEdits(data_dir='4_wikiedits/wikijson')
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
                'p': p_val,
                'arts_per_bucket': con.art_per_bucket_fix
            }
            out_results.append(result)
            print "     " + str(spear) + " spearman corr of concept " + con.name + " with p " + str(p_val)
            del wkedit
        except Exception as e:
            print 'Fatal Error with wiki edits: ' + con.name + ", " + str(con.id) + "; Reason: "+ str(e)
        del con
    outfile = '5_experiment_results/results_exp1_' + now + '_' + str(int(vsize)) + '.json'
    print('Writing results to {}').format(outfile)
    with io.open(outfile, 'a', encoding='utf-8') as f:
        f.write(unicode(json.dumps(out_results, encoding='utf8', ensure_ascii=False)+ '\n'))


# Experiment 2 - Test flexible vector size
def experiment_2(filters, path, vsize):
    print "Experiment 2"
    pref = 'all'
    global filter_id_to_ctg, all_id_to_ctg, all_ctg_to_id, concepts, docid_to_date, weights
    filter_id_to_ctg, all_id_to_ctg = get_ctg(path, filters)
    print filters
    vsize = vsize * 1.0
    all_ctg_to_id = {v:k for k,v in all_id_to_ctg.iteritems()}
    docid_to_date = load_doc_map(path)
    weights = load_idf_weights(path)
    concepts = load_distr(path, pref, filters, filter_id_to_ctg)
    print "Building Concepts"
    for con in concepts:
        try:
            #if len(set(item.split('_')[1] for item in con.features)) < 4: concepts.pop(concepts.index(con)); print "too few articles in " + con.name; continue
            print "Splitting in intervals"
            print len(set(item.split('_')[1] for item in con.features)), math.floor(len(set(item.split('_')[1] for item in con.features))/vsize)
            bucketsize = math.floor(len(set(item.split('_')[1] for item in con.features))/vsize)
            con.into_flex_timeframes(docid_to_date, bucketsize)
            con.rebuild_flex_dist(weights, all_id_to_ctg)
            con.get_cosim()
            #con.print_cosim()
            print "     " + con.name + " built successfully"
        except Exception as e:
            print "Fatal error with concept: " + con.name + ", " + str(con.id) + "; Reason: "+ str(e)
            concepts.pop(concepts.index(con))
    print "Getting edits of " + str(len(concepts)) + " concepts"
    wikiedits = []
    now = str(datetime.datetime.now().date())
    out_results = []
    for con in concepts:
        try:
            wkedit = WikiEdits(data_dir='4_wikiedits/wikijson')
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
                'p': p_val,
                'arts_per_bucket': con.art_per_bucket_flex
            }
            out_results.append(result)
            print "     " + str(spear) + " spearman corr of concept " + con.name + " with p " + str(p_val)
            del wkedit
        except Exception as e:
            print 'Fatal Error with wiki edits: ' + con.name + ", " + str(con.id) + "; Reason: "+ str(e)
        del con
    outfile = '5_experiment_results/results_exp2_' + now + '_' +str(int(vsize)) + '.json'
    print('Writing results to {}').format(outfile)
    with io.open(outfile, 'a', encoding='utf-8') as f:
        f.write(unicode(json.dumps(out_results, encoding='utf8', ensure_ascii=False)+ '\n'))


# Experiment 3 - Test no idf weighting
def experiment_3(filters, path, vsize):
    print "Experiment 3"
    pref = 'all'
    global filter_id_to_ctg, all_id_to_ctg, all_ctg_to_id, concepts, docid_to_date, weights
    filter_id_to_ctg, all_id_to_ctg = get_ctg(path, filters)
    print filters
    vsize = vsize *1.0
    all_ctg_to_id = {v:k for k,v in all_id_to_ctg.iteritems()}
    docid_to_date = load_doc_map(path)
    weights = load_idf_weights(path)
    concepts = load_distr(path, pref, filters, filter_id_to_ctg)
    print "Building Concepts"
    for con in concepts:
        try:
            print "Splitting in intervals"
            bucketsize = math.floor(len(set(item.split('_')[1] for item in con.features))/vsize)
            print len(set(item.split('_')[1] for item in con.features)), bucketsize
            con.into_flex_timeframes(docid_to_date, bucketsize)
            con.rebuild_flex_dist(weights, all_id_to_ctg, weightsON=False)
            con.get_cosim()
            #con.print_cosim()
            print "     " + con.name + " built successfully"
        except Exception as e:
            print "Fatal error with concept: " + con.name + ", " + str(con.id) + "; Reason: "+ str(e)
            concepts.pop(concepts.index(con))
    print "Getting edits of " + str(len(concepts)) + " concepts"
    wikiedits = []
    now = str(datetime.datetime.now().date())
    out_results = []
    for con in concepts:
        try:
            wkedit = WikiEdits(data_dir='4_wikiedits/wikijson')
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
                'p': p_val,
                'arts_per_bucket': con.art_per_bucket_flex
            }
            out_results.append(result)
            print "     " + str(spear) + " spearman corr of concept " + con.name + " with p " + str(p_val)
            del wkedit
        except Exception as e:
            print 'Fatal Error with wiki edits: ' + con.name + ", " + str(con.id) + "; Reason: "+ str(e)
        del con
    outfile = '5_experiment_results/results_exp3_' + now + '_' + str(int(vsize)) + '.json'
    print('Writing results to {}').format(outfile)
    with io.open(outfile, 'a', encoding='utf-8') as f:
        f.write(unicode(json.dumps(out_results, encoding='utf8', ensure_ascii=False)+ '\n'))


# Experiment 4 - Test using kl divergence instead for cosine
def experiment_4(filters, path, vsize):
    print "Experiment 4"
    pref = 'all'
    global filter_id_to_ctg, all_id_to_ctg, all_ctg_to_id, concepts, docid_to_date, weights
    filter_id_to_ctg, all_id_to_ctg = get_ctg(path, filters)
    print filters
    vsize = vsize *1.0
    all_ctg_to_id = {v:k for k,v in all_id_to_ctg.iteritems()}
    docid_to_date = load_doc_map(path)
    weights = load_idf_weights(path)
    concepts = load_distr(path, pref, filters, filter_id_to_ctg)
    print "Building Concepts"
    for con in concepts:
        try:
            print "Splitting in intervals"
            print len(set(item.split('_')[1] for item in con.features)), math.floor(len(set(item.split('_')[1] for item in con.features))/vsize)
            bucketsize = math.floor(len(set(item.split('_')[1] for item in con.features))/vsize)
            con.into_flex_timeframes(docid_to_date, bucketsize)
            con.rebuild_flex_dist(weights, all_id_to_ctg)
            con.get_kl_div()
            print "     " + con.name + " built successfully"
        except Exception as e:
            print "Fatal error with concept: " + con.name + ", " + str(con.id) + "; Reason: "+ str(e)
            concepts.pop(concepts.index(con))
    print "Getting edits of " + str(len(concepts)) + " concepts"
    wikiedits = []
    now = str(datetime.datetime.now().date())
    out_results = []
    for con in concepts:
        try:
            wkedit = WikiEdits(data_dir='4_wikiedits/wikijson')
            wikiedits.append(wkedit)
            wkedit.parse(con.name)
            wkedit.split_revisions(con.flexIntervals)
            if len(wkedit.rev_tf_sums) == 0: continue
            spear, p_val = comparator(con.kl_div, wkedit.rev_tf_sums)
            result = {
                'concept': con.name,
                'id': con.id,
                'intervals': [str(dt.date()) for dt in con.flexIntervals],
                'kl_div': con.kl_div,
                'wkedits': wkedit.rev_tf_sums,
                'spearman': spear,
                'p': p_val,
                'arts_per_bucket': con.art_per_bucket_flex
            }
            out_results.append(result)
            print "     " + str(spear) + " spearman corr of concept " + con.name + " with p " + str(p_val)
            del wkedit
        except Exception as e:
            print 'Fatal Error with wiki edits: ' + con.name + ", " + str(con.id) + "; Reason: "+ str(e)
        del con
    outfile = '5_experiment_results/results_exp4_' + now + '_' + str(int(vsize)) + '.json'
    print('Writing results to {}').format(outfile)
    with io.open(outfile, 'a', encoding='utf-8') as f:
        f.write(unicode(json.dumps(out_results, encoding='utf8', ensure_ascii=False)+ '\n'))


# Experiment 5 - Test unsing 24 flexible vectors
def experiment_5(filters, path):
    print "Experiment 5"
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
            print "Splitting in intervals"
            print len(set(item.split('_')[1] for item in con.features)), math.floor(len(set(item.split('_')[1] for item in con.features))/24.0)
            bucketsize = math.floor(len(set(item.split('_')[1] for item in con.features))/24.0)
            con.into_flex_timeframes(docid_to_date, bucketsize)
            con.rebuild_flex_dist(weights, all_id_to_ctg)
            con.get_kl_div()
            print "     " + con.name + " built successfully"
        except Exception as e:
            print "Fatal error with concept: " + str(e)
            concepts.pop(concepts.index(con))
    print "Getting edits of " + str(len(concepts)) + " concepts"
    wikiedits = []
    now = str(datetime.datetime.now().date())
    out_results = []
    for con in concepts:
        try:
            wkedit = WikiEdits(data_dir='4_wikiedits/wikijson')
            wikiedits.append(wkedit)
            wkedit.parse(con.name)
            wkedit.split_revisions(con.flexIntervals)
            if len(wkedit.rev_tf_sums) == 0: continue
            spear, p_val = comparator(con.kl_div, wkedit.rev_tf_sums)
            result = {
                'concept': con.name,
                'id': con.id,
                'intervals': [str(dt.date()) for dt in con.flexIntervals],
                'kl_div': con.kl_div,
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
    outfile = '5_experiment_results/results_exp5_' + now + '.json'
    print('Writing results to {}').format(outfile)
    with io.open(outfile, 'a', encoding='utf-8') as f:
        f.write(unicode(json.dumps(out_results, encoding='utf8', ensure_ascii=False)+ '\n'))


# Experiment 6 - Test one publisher at a time vs wikipedia
def experiment_6(filters, path):
    print "Experiment 4"
    prefs = ['DM', 'IND', 'WP', 'NYT', 'HP']
    for pref in prefs:
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
            except Exception as e:
                print "Fatal error with concept: " + con.name + ", " + str(con.id) + "; Reason: "+ str(e)
                concepts.pop(concepts.index(con))
        print "Getting edits of " + str(len(concepts)) + " concepts"
        wikiedits = []
        now = str(datetime.datetime.now().date())
        out_results = []
        for con in concepts:
            try:
                wkedit = WikiEdits(data_dir='4_wikiedits/wikijson')
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
            except Exception as e:
                print 'Fatal Error with wiki edits: ' + con.name + ", " + str(con.id) + "; Reason: "+ str(e)
            del con
        outfile = '5_experiment_results/results_exp5_' + now + '.json'
        print('Writing results to {}').format(outfile)
        with io.open(outfile, 'a', encoding='utf-8') as f:
            f.write(unicode(json.dumps(out_results, encoding='utf8', ensure_ascii=False)+ '\n'))


if __name__ == "__main__":
    experiment_1(random.sample(xrange(71564), 6))