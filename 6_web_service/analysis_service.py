import csv, itertools
import sys
from sklearn.metrics import pairwise as pw
import warnings
import time
import datetime, json
from flask import Flask, jsonify, render_template, request
warnings.filterwarnings("ignore")
csv.field_size_limit(sys.maxsize)

# Parse arguments
path = sys.argv[1]
publisher = sys.argv[2]

# Init global vars
all_concepts = []
all_id_to_ctg, docid_to_date, weights = {}, {}, {}
DATEONE = datetime.datetime.strptime("2014-08-14", "%Y-%m-%d")
DATELAST = datetime.datetime.strptime("2015-08-14", "%Y-%m-%d")

# Flask
app = Flask(__name__)



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
        self.core_set = set()
        self.serialized = ''
    def into_fixed_timeframes(self):
        buckets = 12
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
        self.docID_fixFrames = all_tag_docs
        #assert len(self.fixIntervals) == len(self.fixFrames) == len(self.docID_fixFrames), "Different amount of fix vector elements!"
    def into_flex_timeframes(self, bucketsize):
        tag_quad = [[int(item.split('_')[0]), int(item.split('_')[1]), datetime.datetime.strptime(docid_to_date[int(item.split('_')[1])], "%Y-%m-%d"), 1] for item in self.features]
        tag_quad = sorted(tag_quad, key=lambda date: (date[2], date[1]))
        tag_len = len(set([tag[1] for tag in tag_quad]))
        if tag_len <= 2 * bucketsize: buckets=2
        else: buckets = int(round(tag_len/(1.0 * bucketsize)))
        tmpbucketsize = int(round(tag_len / (1.0 * buckets)))
        all_buckets = [dict() for x in range(buckets)]
        all_last_adds = buckets * [time.strptime("2015-08-14", "%Y-%m-%d")]
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
            if i > tmpbucketsize:
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
            self.flexIntervals.append(str(last_add)[:10])
        self.docID_flexFrames = all_tag_docs
        #assert len(self.flexIntervals) == len(self.flexFrames) == len(self.docID_flexFrames), "Different amount of flex vector elements!"
    def rebuild_flex_dist(self):
        vlen = len(all_id_to_ctg)
        for d_vec in self.flexFrames:
            d_vector = [0.00001] * vlen
            for keyval in d_vec:
                d_vector[keyval[0]] = keyval[1] * weights[keyval[0]]
            self.flexVector.append(d_vector)
    def rebuild_fix_dist(self):
        vlen = len(all_id_to_ctg)
        for d_vec in self.fixFrames:
            d_vector = [0.00001] * vlen
            for keyval in d_vec:
                d_vector[keyval[0]] = keyval[1] * weights[keyval[0]]
            self.fixVector.append(d_vector)
    def get_cosim(self):
        distr = self.flexVector
        emptbucks = 0
        for i in range(0,len(distr)-1):
            this_distr = distr[i]
            next_distr = distr[i+1]
            if sum(this_distr) < 1 or sum(next_distr) < 1:
                emptbucks +=1
                self.cosim.append("NaN")
                continue
            this_entropy = pw.cosine_similarity(this_distr, next_distr)
            self.cosim.append(this_entropy)
        #assert len(self.cosim) == len(self.flexFrames) - 1, "Every window should have one value!"
    def get_top_x(self, top_x):
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
            core = []
            for idx, a in enumerate(zip(this_cnt, next_cnt)):
                if bool(a[0]) and bool(a[1]):
                    core.append([a[1], idx])
            top_adds = [[all_id_to_ctg[idx][28:], a] for a, idx in sorted(additions, reverse=True)]
            if len(top_adds) >= top_x: top_adds = top_adds[:top_x]
            top_rem = [[all_id_to_ctg[idx][28:], a] for a, idx in sorted(removals, reverse=True)]
            if len(top_rem) >= top_x: top_rem= top_rem[:top_x]
            top_core = [[all_id_to_ctg[idx][28:],a] for a, idx in sorted(core, reverse=True)]
            if len(top_core) >= top_x: top_core= top_core[:top_x]
            self.top_adds.append(top_adds)
            self.top_removals.append(top_rem)
            self.top_core.append(top_core)
        assert len(self.top_adds) == len(self.top_core) == len(self.top_removals) == len(self.fixVector)-1, "Every window should have one value!"
    def serialize(self):
        print self.top_adds
        self.serialized = {
            'id': self.id,
            'name': self.name,
            'cosines': [{'date':self.flexIntervals[t], 'cosine': self.cosim[t][0][0]} for t in range(len(self.cosim))],
            'top_core': [{'date':str(self.fixIntervals[t]), 'key':self.top_core[t][k][0], 'value':self.top_core[t][k][1]} for t,k in itertools.product(range(len(self.top_core)), range(min([len(t) for t in self.top_core])))],
            'top_adds': [{'date':str(self.fixIntervals[t]), 'key':self.top_adds[t][k][0], 'value':self.top_adds[t][k][1]} for t,k in itertools.product(range(len(self.top_adds)), range(min([len(t) for t in self.top_adds])))],
            'top_rems': [{'date':str(self.fixIntervals[t]), 'key':self.top_removals[t][k][0], 'value':self.top_removals[t][k][1]} for t,k in itertools.product(range(len(self.top_removals)), range(min([len(t) for t in self.top_removals])))]
        }
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
        self.core_set = set()



def get_ctg():
    all_id_to_ctg = {}
    with open(path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_id_to_ctg[int(row[1])] = row[0]
    return all_id_to_ctg, all_id_to_ctg


def load_doc_map():
    docid_to_date = {}
    with open(path + 'docid_to_date.csv') as docmap:
        reader = csv.reader(docmap, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            docid_to_date[int(row[0])] = row[1]
    return docid_to_date


def load_idf_weights():
    filter_id_to_weight = {}
    with open(path + "all_distributions_weights.csv") as weights_map:
        reader = csv.reader(weights_map, delimiter=',', quotechar='|',quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            filter_id_to_weight[int(row[0])] = float(row[1])
    return filter_id_to_weight

# technically, we want everything in memory, but thats for later
def load_distr():
    all_d_content = []
    with open(path + publisher + '_distributions_time.csv') as distr_vec:
        reader = csv.reader(distr_vec, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        all_data = []
        for row in reader:
            all_data.append([int(row[0]),row[1:]])
            if len(all_data)>135: break
    for item in all_data:
        tups = []
        for i in range(0,len(item[1])-2,2):
            tups.append(item[1][i])
        this_concept = Concept(item[0], filter_id_to_ctg[item[0]].split('/')[-1],tups)
        all_d_content.append(this_concept)
    return all_d_content


def pretty_print(concept):
    print "Cosine Sim within filter " + concept.name + " are: "
    for i in range(len(concept.flexIntervals)-1):
        if concept.cosim[i] =="NaN": continue
        print "     Window " + str(concept.flexIntervals[i]) + " to " + str(concept.flexIntervals[i+1]) + ": " + str(concept.cosim[i])
    print "Core + Changes on a monthly basis: "
    for i in range(len(concept.fixIntervals)-1):
        print "     Window " + str(concept.fixIntervals[i]) + " to " + str(concept.fixIntervals[i+1]) + ":"
        print "         Top adds: " + str(concept.top_adds[i])  + " \n         Top rems: " + str(concept.top_removals[i])  \
              + "\n         Top core: " + str(concept.top_core[i])


def format_core(con):
    printlist = []
    con.top_core = normalize_context(con.top_core)
    core_no_key = []
    for i in range(len(con.top_core)):
        core_no_key.append([t[0] for t in con.top_core[i]])
        for j in range(len(con.top_core[0])):
            if len(con.top_core[i][j][0]) == 0: continue
            con.core_set.add(con.top_core[i][j][0])
    for core_item in con.core_set:
        for j in range(len(con.top_core)):
            if core_item in core_no_key[j]:
                printlist.append([core_item, con.top_core[j][core_no_key[j].index(core_item)][1], con.fixIntervals[j].date()])
            else:
                printlist.append([core_item, 1, con.fixIntervals[j].date()])
    #writer.writerow(['key','value','date'])
    #for core in printlist:
    #    writer.writerow(core)


def format_adds(con):
    printlist = {t:[] for t in con.fixIntervals}
    add_no_key = []
    con.core_set = set()
    con.top_adds = normalize_context(con.top_adds)
    print con.top_adds
    for i in range(len(con.top_adds)):
        add_no_key.append([t[0] for t in con.top_adds[i]])
        for j in range(len(con.top_adds[i])):
            if len(con.top_adds[i][j][0]) == 0: continue
            con.core_set.add(con.top_adds[i][j][0])
    for core_item in con.core_set:
        for j in range(len(con.top_adds)):
            if core_item in add_no_key[j]:
                printlist[con.fixIntervals[j]].append({core_item: con.top_adds[j][add_no_key[j].index(core_item)][1]})
            else:
                printlist[con.fixIntervals[j]].append({core_item: 0})
    #writer.writerow(["Date"] + list(con.core_set))
    f = []
    for k,p in printlist.iteritems():
        tmp = [k.date()]
        for v in p:
            tmp.append(v.values()[0])
        f.append(tmp)
    f = sorted(f, key=lambda k:k[0])
    #writer.writerows(f)


def format_rems(con):
    printlist = {t:[] for t in con.fixIntervals}
    rem_no_key = []
    con.core_set = set()
    con.top_removals = normalize_context(con.top_removals)
    for i in range(len(con.top_removals)):
        rem_no_key.append([t[0] for t in con.top_removals[i]])
        for j in range(len(con.top_removals[i])):
            if len(con.top_removals[i][j][0]) == 0: continue
            con.core_set.add(con.top_removals[i][j][0])
    for core_item in con.core_set:
        for j in range(len(con.top_removals)):
            if core_item in rem_no_key[j]:
                printlist[con.fixIntervals[j]].append({core_item: con.top_removals[j][rem_no_key[j].index(core_item)][1]})
            else:
                printlist[con.fixIntervals[j]].append({core_item: 0})
    #writer.writerow(["Date"] + list(con.core_set))
    f = []
    for k,p in printlist.iteritems():
        tmp = [k.date()]
        for v in p:
            tmp.append(v.values()[0])
        f.append(tmp)
    f = sorted(f, key=lambda d:d[0])
    #writer.writerows(f)


def normalize_context(context):
    for i in range(len(context)):
        total = float(sum(t[1] for t in context[i]))
        for j in range(len(context[i])):
            context[i][j][1] = float("{0:.2f}".format((context[i][j][1]/total)*100))
    return context


def preload():
    print "Preloading data"
    global filter_id_to_ctg, all_id_to_ctg, concepts, docid_to_date, weights, all_concepts
    filter_id_to_ctg, all_id_to_ctg = get_ctg()
    docid_to_date = load_doc_map()
    weights = load_idf_weights()
    all_concepts = load_distr()


def filter_concept(filter_id, bucketsize, top_x):
    con = all_concepts[filter_id]
    con.into_fixed_timeframes()
    con.into_flex_timeframes(bucketsize)
    con.rebuild_flex_dist()
    con.rebuild_fix_dist()
    con.get_cosim()
    con.get_top_x(top_x)

    #format_core(con)
    #format_adds(con)
    #format_rems(con)

    con.serialize()
    return con.serialized


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/_filter', methods=['GET'])
def filter_request():
    filter_id = int(request.args.get('filter_id',0,type=str))
    bucketsize = int(request.args.get('bucketsize',0,type=str))
    top_x = int(request.args.get('top_x',0,type=str))
    result = filter_concept(filter_id, bucketsize, top_x)
    return jsonify(result)


@app.route('/test_filter')
def test_filter():
    filter_id = 37
    bucketsize = 5
    top_x = 2
    result = filter_concept(filter_id, bucketsize, top_x)
    print result
    return json.dumps(result)


if __name__ == "__main__":
    preload()
    app.run(host='0.0.0.0', port=8080, debug=True)


