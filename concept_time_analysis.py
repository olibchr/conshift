import csv, math
import sys
from sklearn.metrics import pairwise as pw
import warnings
import time
import datetime
import scipy.stats as sstats
warnings.filterwarnings("ignore")
csv.field_size_limit(sys.maxsize)

# Init global vars
concepts = []
filter_id_to_ctg, all_id_to_ctg, all_ctg_to_id, docid_to_date, weights = {}, {}, {}, {}, {}
DATEONE = datetime.datetime.strptime("2014-08-14", "%Y-%m-%d")
DATELAST = datetime.datetime.strptime("2015-08-14", "%Y-%m-%d")

class Concept():
    def __init__(self, id, name, features):
        self.id = id
        self.name = name
        self.features = features
        self.docID_fixFrames = []
        self.fixFrames = []
        self.fixVector = []
        self.fixIntervals = []
        self.docID_flexFrames = []
        self.flexFrames = []
        self.flexVector = []
        self.flexIntervals = []
        self.cosim = []
        self.top_adds = []
        self.top_removals = []
        self.top_core = []
        self.art_per_bucket_fix = []
        self.art_per_bucket_flex = []
        self.core_set = set()
    def into_fixed_timeframes(self, docid_to_date, buckets):
        tag_quad = [[int(item.split('_')[0]), int(item.split('_')[1]), datetime.datetime.strptime(docid_to_date[int(item.split('_')[1])], "%Y-%m-%d"), 1] for item in self.features]
        tag_quad = sorted(tag_quad, key=lambda date: (date[2], date[1]))
        timedelta = DATELAST - DATEONE
        self.fixIntervals = [(DATEONE + (a * timedelta/buckets)) for a in range(1,buckets+1)]
        all_buckets = [dict() for x in range(buckets)]
        all_tag_docs = [[]] * buckets
        for tag in tag_quad:
            i = 0
            while(tag[2]>self.fixIntervals[i]):
                i +=1
            if tag[0] in all_buckets[i]:
                all_buckets[i][tag[0]] = all_buckets[i][tag[0]] + tag[3]
            else: all_buckets[i][tag[0]] = tag[3]
            all_tag_docs[i].append(tag[1])
        for this_bucket, last_add in zip(all_buckets, self.fixIntervals):
            self.fixFrames.append([k, v] for k, v in this_bucket.iteritems())
            self.art_per_bucket_fix.append(len(this_bucket))
        self.docID_fixFrames = all_tag_docs
        assert len(self.fixIntervals) == len(self.fixFrames) == len(self.docID_fixFrames), "Different amount of fix vector elements!"
    def into_flex_timeframes(self, docid_to_date, bucketsize):
        tag_quad = [[int(item.split('_')[0]), int(item.split('_')[1]), datetime.datetime.strptime(docid_to_date[int(item.split('_')[1])], "%Y-%m-%d"), 1] for item in self.features]
        tag_quad = sorted(tag_quad, key=lambda date: (date[2], date[1]))
        tag_len = len(set([tag[1] for tag in tag_quad]))
        if tag_len <= 2 * bucketsize: buckets=2
        else: buckets = int(math.ceil(tag_len/(1.0 * bucketsize)))
        all_buckets = [dict() for x in range(buckets)]
        all_last_adds = buckets * [datetime.datetime.strptime("2015-08-14", "%Y-%m-%d")]
        i = 0
        t = 0
        this_bucket = all_buckets[0]
        last_tag_doc = tag_quad[0][1]
        all_tag_docs = [[]] * buckets
        for tag in tag_quad:
            tag_id = tag[0]
            tag_doc = tag[1]
            tag_date = tag[2]
            tag_cnt = tag[3]
            if i >= bucketsize:
                i = 0
                t += 1
                this_bucket = all_buckets[t]
            all_last_adds[t] = tag_date
            if last_tag_doc != tag_doc:
                i+=1
                last_tag_doc = tag_doc
            if tag_id in this_bucket:
                this_bucket[tag_id] = this_bucket[tag_id] + tag_cnt
            else:
                this_bucket[tag_id] = tag_cnt
            all_tag_docs[t].append(tag_doc)
        for this_bucket, last_add in zip(all_buckets, all_last_adds):
            self.flexFrames.append([k, v] for k, v in this_bucket.iteritems())
            self.art_per_bucket_flex.append(len(this_bucket))
            self.flexIntervals.append(last_add)
        self.docID_flexFrames = all_tag_docs
        self.flexIntervals[-1] = datetime.datetime.strptime("2015-08-14", "%Y-%m-%d")  # very last add must be last date, otherwise thatll clash with wikipedia edits
        assert len(self.flexIntervals) == len(self.flexFrames) == len(self.docID_flexFrames), "Different amount of flex vector elements!"
    def rebuild_flex_dist(self, weights, all_id_to_ctg, weightsON= True):
        vlen = len(all_id_to_ctg)
        for d_vec in self.flexFrames:
            d_vector = [0.00001] * vlen
            for keyval in d_vec:
                if weightsON == True:
                    d_vector[keyval[0]] = keyval[1] * weights[keyval[0]]
                else:
                    d_vector[keyval[0]] = keyval[1]
            self.flexVector.append(d_vector)
    def rebuild_fix_dist(self, weights, all_id_to_ctg):
        vlen = len(all_id_to_ctg)
        for d_vec in self.fixFrames:
            d_vector = [0.00001] * vlen
            for keyval in d_vec:
                d_vector[keyval[0]] = keyval[1] * weights[keyval[0]]
            self.fixVector.append(d_vector)
    def get_cosim(self, vector = "flex"):
        if vector == "flex": distr = self.flexVector
        elif vector == "fix": distr = self.fixVector
        else: print " wrong vector selection"
        for i in range(0,len(distr)-1):
            this_distr = distr[i]
            next_distr = distr[i+1]
            this_entropy = pw.cosine_similarity(this_distr, next_distr)
            self.cosim.append(this_entropy[0][0])
    def get_kl_div(self, vector='flex'):
        if vector == 'flex': distr = self.flexVector
        elif vector == 'fix': distr = self.fixVector
        else: print "Error: Bad vector selection"
        self.kl_div = []
        for i in range(0,len(distr)-1):
            this_distr = distr[i]
            next_distr = distr[i+1]
            this_divergence = sstats.entropy(this_distr, next_distr)
            self.kl_div.append(this_divergence)
    def get_core(self):
        distr = self.fixVector
        emptbucks = 0
        for i in range(0,len(distr)-1):
            this_distr = distr[i]
            next_distr = distr[i+1]
            if sum(this_distr) < 1 or sum(next_distr) < 1:
                emptbucks +=1
                print "Critical amount of articles per bucket"
            this_cnt = [int(i) if i > 0.0001 else 0 for i in this_distr]
            next_cnt = [int(i) if i > 0.0001 else 0 for i in next_distr]
            additions = []
            for idx, a in enumerate(zip(this_cnt, next_cnt)):
                if not bool(a[0]) and bool(a[1]):
                    additions.append([a[1], idx])
            removals = []
            rsum = 0
            for idx, a in enumerate(zip(this_cnt, next_cnt)):
                if bool(a[0]) and not bool(a[1]):
                    rsum += a[0]
                    removals.append([a[0], idx])
            print rsum
            core = []
            for idx, a in enumerate(zip(this_cnt, next_cnt)):
                if bool(a[0]) and bool(a[1]):
                    core.append([a[1], idx])
            top_adds = [[all_id_to_ctg[idx][28:], a] for a, idx in sorted(additions, reverse=True)]
            if len(top_adds) >= 5: top_adds = top_adds[:5]
            top_rem = [[all_id_to_ctg[idx][28:], a] for a, idx in sorted(removals, reverse=True)]
            if len(top_rem) >= 5:
                top_rem= top_rem[:5]
            top_core = [[all_id_to_ctg[idx],a] for a, idx in sorted(core, reverse=True)]
            if len(top_core) >= 5: top_core= top_core[:5]
            print top_core
            self.top_adds.append(top_adds)
            self.top_removals.append(top_rem)
            self.top_core.append(top_core)
        assert len(self.top_adds) == len(self.top_core) == len(self.top_removals) == len(self.fixVector)-1, "Every window should have one value!"
    def print_cosim(self):
        print "Cosine Sim within filter " + self.name + " are: "
        for i in range(len(self.flexIntervals)-1):
            if self.cosim[i] =="NaN": continue
            print "     Window " + str(self.flexIntervals[i]) + " to " + str(self.flexIntervals[i+1]) + ": " + str(self.cosim[i])


def get_ctg(path, filters):
    filter_id_to_ctg = {}
    all_id_to_ctg = {}
    with open(path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            if int(row[1]) in filters:
                filter_id_to_ctg[int(row[1])] = row[0]
            all_id_to_ctg[int(row[1])] = row[0]
    return filter_id_to_ctg, all_id_to_ctg


def load_doc_map(path):
    docid_to_date = {}
    with open(path + 'docid_to_date.csv') as docmap:
        reader = csv.reader(docmap, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            docid_to_date[int(row[0])] = row[1]
    return docid_to_date


def load_idf_weights(path):
    filter_id_to_weight = {}
    with open(path + "all_distributions_weights.csv") as weights_map:
        reader = csv.reader(weights_map, delimiter=',', quotechar='|',quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            filter_id_to_weight[int(row[0])] = float(row[1])
    return filter_id_to_weight


def load_distr(path, pref, filters, filter_id_to_ctg):
    all_d_content = []
    with open(path + pref + '_distributions_time.csv') as distr_vec:
        reader = csv.reader(distr_vec, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        all_data = []
        for row in reader:
            if int(row[0]) not in filters: continue
            all_data.append([int(row[0]),row[1:]])
            if len(all_data) == len(filters):
                del reader
                break
    for item in all_data:
        tups = []
        for i in range(0,len(item[1])-2,2):
            # change this to
            tups.append(item[1][i])
            #tups.append((item[1][i], int(item[1][i+1])))
        try:
            this_concept = Concept(item[0], filter_id_to_ctg[item[0]].split('/')[-1],tups)
            print "     " + str(this_concept.id) + ": " + this_concept.name + " with " + str(len(this_concept.features)) + ' annotations in ' + str(len(set(item.split('_')[1] for item in this_concept.features))) + ' articles.'
            all_d_content.append(this_concept)
        except KeyError: print str(item[0]) + " couldn't be found"
    return all_d_content


def pretty_print():
    for concept in concepts:
        print "Cosine Sim within filter " + concept.name + " are: "
        for i in range(len(concept.flexIntervals)-1):
            if concept.cosim[i] =="NaN": continue
            print "     Window " + str(concept.flexIntervals[i]) + " to " + str(concept.flexIntervals[i+1]) + ": " + str(concept.cosim[i])
        print "Core + Changes on a monthly basis: "
        for i in range(len(concept.fixIntervals)-1):
            print "     Window " + str(concept.fixIntervals[i]) + " to " + str(concept.fixIntervals[i+1]) + ":"
            print "         Top adds: " + str(concept.top_adds[i])  + " \n         Top rems: " + str(concept.top_removals[i])  \
                  + "\n         Top core: " + str(concept.top_core[i])


def save_state():
    with open('2_results/analysis_results_' + ''.join(map(str,filters)) + '.csv', 'wb') as out:
        writer = csv.writer(out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for con in concepts:
            for i in range(len(con.fixIntervals)-1):
                flat_topcore = [val for sublist in con.top_core[i] for val in sublist]
                flat_topadds = [val for sublist in con.top_adds[i] for val in sublist]
                flat_toprems = [val for sublist in con.top_adds[i] for val in sublist]
                print_list = [con.id, con.name, con.intervals[i], con.cosim[i][0][0]] + flat_topcore + flat_topadds + flat_toprems
                writer.writerow(print_list)


def save_core(filters):
    with open('2_results/analysis_core' + ''.join(map(str,filters)) + '.csv', 'wb') as out:
        writer = csv.writer(out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        printlist = []
        for con in concepts:
            #con.top_core = norm_cont(con.top_core)
            core_no_key = []
            for i in range(len(con.top_core)):
                core_no_key.append([t[0] for t in con.top_core[i]])
                for j in range(len(con.top_core[i])):
                    if not con.top_core[i][j][0]: continue
                    con.core_set.add(con.top_core[i][j][0])
            for core_item in con.core_set:
                for j in range(len(con.top_core)):
                    if core_item in core_no_key[j]:
                        printlist.append([core_item, con.top_core[j][core_no_key[j].index(core_item)][1], con.fixIntervals[j].date()])
                    else:
                        vval = all_ctg_to_id[core_item]
                        val = con.fixVector[j][vval]
                        printlist.append([core_item, val, con.fixIntervals[j].date()])
        writer.writerow(['key','value','date'])
        for core in printlist:
            writer.writerow(core)


def save_core_bars(filters):
    with open('2_results/analysis_core_bars' + ''.join(map(str,filters)) + '.csv', 'wb') as out:
        for con in concepts:
            writer = csv.writer(out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            printlist = {t:[] for t in con.fixIntervals}
            core_no_key = []
            con.core_set = set()
            for i in range(len(con.top_core)):
                core_no_key.append([t[0] for t in con.top_core[i]])
                for j in range(len(con.top_core[i])):
                    if not con.top_core[i][j][0]: continue
                    con.core_set.add(con.top_core[i][j][0])
            for core_item in con.core_set:
                for j in range(len(con.top_adds)):
                    if core_item in core_no_key[j]:
                        printlist[con.fixIntervals[j]].append({core_item: con.top_core[j][core_no_key[j].index(core_item)][1]})
                    else:
                        printlist[con.fixIntervals[j]].append({core_item: 0})
            assert len(con.core_set) != 0, "No data for con  " + con.name
            writer.writerow(["Date"] + list(con.core_set))

            f = []
            for k,p in printlist.iteritems():
                tmp = [k]
                for v in p:
                    tmp.append(v.values()[0])
                #assert len(tmp)>1, "No data to write into bar output file for date " + str(k)
                f.append(tmp)
            f = sorted(f, key=lambda k:k[0])
            writer.writerows(f)


def save_adds(filters):
    with open('2_results/analysis_adds' + ''.join(map(str,filters)) + '.csv', 'wb') as out:
        for con in concepts:
            writer = csv.writer(out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            printlist = {t:[] for t in con.fixIntervals}
            add_no_key = []
            con.core_set = set()
            con.top_adds = norm_cont(con.top_adds)
            for i in range(len(con.top_adds)):
                add_no_key.append([t[0] for t in con.top_adds[i]])
                for j in range(len(con.top_adds[i])):
                    if not con.top_adds[i][j][0]: continue
                    con.core_set.add(con.top_adds[i][j][0])
            for core_item in con.core_set:
                for j in range(len(con.top_adds)):
                    if core_item in add_no_key[j]:
                        printlist[con.fixIntervals[j]].append({core_item: con.top_adds[j][add_no_key[j].index(core_item)][1]})
                    else:
                        printlist[con.fixIntervals[j]].append({core_item: 0})
            writer.writerow(["Date"] + list(con.core_set))

            f = []
            for k,p in printlist.iteritems():
                tmp = [k.date()]
                for v in p:
                    tmp.append(v.values()[0])
                f.append(tmp)
            f = sorted(f, key=lambda k:k[0])
            writer.writerows(f)


def save_rems(filters):
    with open('2_results/analysis_rems' + ''.join(map(str,filters)) + '.csv', 'wb') as out:
        for con in concepts:
            writer =  csv.writer(out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            printlist = {t:[] for t in con.fixIntervals}
            rem_no_key = []
            con.core_set = set()
            con.top_removals = norm_cont(con.top_removals)
            for i in range(len(con.top_removals)):
                rem_no_key.append([t[0] for t in con.top_removals[i]])
                for j in range(len(con.top_removals[i])):
                    if not con.top_removals[i][j][0]: continue
                    con.core_set.add(con.top_removals[i][j][0])
            for core_item in con.core_set:
                for j in range(len(con.top_removals)):
                    if core_item in rem_no_key[j]:
                        printlist[con.fixIntervals[j]].append({core_item: con.top_removals[j][rem_no_key[j].index(core_item)][1]})
                    else:
                        printlist[con.fixIntervals[j]].append({core_item: 0})
            writer.writerow(["Date"] + list(con.core_set))
            f = []
            for k,p in printlist.iteritems():
                tmp = [k.date()]
                for v in p:
                    tmp.append(v.values()[0])
                f.append(tmp)
            f = sorted(f, key=lambda d:d[0])
            writer.writerows(f)


def norm_cont(context):
    for i in range(len(context)):
        total = float(sum(t[1] for t in context[i]))
        for j in range(len(context[i])):
            context[i][j][1] = float("{0:.2f}".format((context[i][j][1]/total)*100))
    return context


def main():
    # Parse arguments
    path = sys.argv[1]
    pref = sys.argv[2]
    buckets = int(sys.argv[3])
    filters = map(int, sys.argv[4:])
    print "Setting filters.. "
    global filter_id_to_ctg, all_id_to_ctg, all_ctg_to_id, concepts, docid_to_date, weights
    filter_id_to_ctg, all_id_to_ctg = get_ctg(path, filters)
    all_ctg_to_id = {v:k for k,v in all_id_to_ctg.iteritems()}
    docid_to_date = load_doc_map(path)
    weights = load_idf_weights(path)
    concepts = load_distr(path, pref, filters, filter_id_to_ctg)
    print "Building Concepts"
    for con in concepts:
        bucketsize = len(set(item.split('_')[1] for item in con.features))/buckets
        con.into_fixed_timeframes(docid_to_date, buckets)
        con.into_flex_timeframes(docid_to_date, bucketsize)
        con.rebuild_flex_dist(weights, all_id_to_ctg)
        con.rebuild_fix_dist(weights, all_id_to_ctg)
        con.get_cosim()
        con.get_core()
        #print con.flexIntervals
        #print len(con.flexIntervals)
        #pretty_print()
        #save_state()
        save_core(filters)
        #save_core_bars(filters)
        #save_adds(filters)
        #save_rems(filters)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Not enough arguments"
    else:
        main()


