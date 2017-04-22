import csv, operator
import sys, time, string
from datetime import datetime
from itertools import chain

if len(sys.argv) < 2:
    print "Give dir path to annotion files!"
    exit()
path = sys.argv[1]
spec = sys.argv[2]

"""
This program builds concept distributions vectors for a time analysis
"""

def get_items():
    all_annotations_id = []
    all_annotations_doc = []
    with open(path + spec + '_annotation_vectors.csv') as annotation_vectors:
        reader = csv.reader(annotation_vectors, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        last_id = 0
        this_id_list = []
        doc_to_id = {}
        provide_id = 0
        for item in reader:
            this_id = int(item[0])
            if item[1] not in doc_to_id:
                doc_to_id[item[1]] = provide_id
                provide_id += 1
            if last_id == this_id:
                this_id_list.append([int(item[0]), doc_to_id[item[1]], time.strptime(item[2], "%Y-%m-%d")])
            else:
                all_annotations_id.append(this_id_list)
                last_id = this_id
                this_id_list = []
                this_id_list.append([int(item[0]), doc_to_id[item[1]], time.strptime(item[2], "%Y-%m-%d")])
            all_annotations_doc.append([doc_to_id[item[1]], int(item[0]), time.strptime(item[2], "%Y-%m-%d")])
    return all_annotations_id[1:], sorted(all_annotations_doc[1:], key=lambda docid: docid[0]), doc_to_id


def doc_mapping(all_annotations):
    all_annotations_doc = []
    last_doc = all_annotations[0][0]
    this_doc_list = []
    for item in all_annotations:
        this_doc = item[0]
        if last_doc == this_doc:
            this_doc_list.append(item)
        else:
            all_annotations_doc.append(this_doc_list)
            last_doc = this_doc
            this_doc_list = []
            this_doc_list.append(item)
    return all_annotations_doc


def build_vectors(all_annotations_id, all_annotations_doc):
    i = 0
    all_d_vector = []
    doc_id_to_date = {}
    doc_match_list = {all_annotations_doc[i][0][0]: i for i in range(len(all_annotations_doc))}
    outfile = open(path + spec + '_distributions_time.csv', 'wb')
    writer = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for ids in all_annotations_id:
        if i % 500 == 0:
            print "progress: " + str(i) + ", " + str(len(all_annotations_id)) + ", " + str(
                (i * 100) / float(1.0 * len(all_annotations_id))) + "%"
            #if i != 0: break
        i += 1
        vector = {}
        indeces = []
        for item in ids:
            docid = item[1]
            try:
                doc = all_annotations_doc[doc_match_list[docid]]
            except KeyError:
                print "key error"
                continue
            for doc_w_docid in doc:
                dtime = datetime(*doc[0][2][:6]).isoformat()[:10]
                vector[str(doc_w_docid[1]) + '_' + str(doc_w_docid[0])] = 1
                doc_id_to_date[doc_w_docid[0]] = dtime
        for k, v in vector.iteritems():
            indeces.append([k])
        tmp = list(chain.from_iterable(indeces))
        writer.writerow([int(ids[0][0])] + tmp)
        #all_d_vector.append([int(ids[0][0]), indeces])
    return all_d_vector, doc_id_to_date


def main():
    print "Loading Items"
    all_annotations_id, all_annotations_doc, doc_to_id = get_items()
    all_annotations_doc = doc_mapping(all_annotations_doc)
    print "Building Distributions"
    all_d_vecs_time, doc_id_to_date = build_vectors(all_annotations_id, all_annotations_doc)
    """with open('all_distributions_time.csv', 'wb') as out_file:
        writer = csv.writer(out_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for line in all_d_vecs_time:
            tmp = list(chain.from_iterable(line[1]))
            writer.writerow([line[0]] + tmp)"""
    if spec != 'ALL': exit()
    with open('docid_to_date.csv', 'wb') as out_file:
        writer = csv.writer(out_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for k,v in doc_id_to_date.iteritems():
            writer.writerow([k,v.encode('utf-8')])
    with open('doc_to_id.csv','wb') as out_file:
        writer = csv.writer(out_file, delimiter=',')
        for k,v in doc_to_id.iteritems():
            writer.writerow([k,v])

if __name__ == "__main__":
    main()


