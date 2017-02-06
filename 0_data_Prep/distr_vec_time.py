import csv, operator
import sys, time, string
from datetime import datetime
from itertools import chain

if len(sys.argv) < 2:
    print "Give dir path to annotion files!"
    exit()
path = sys.argv[1]


def get_ctg():
    all_id_to_ctg = {}
    with open(path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_id_to_ctg[int(row[1])] = row[0]
    return all_id_to_ctg, all_id_to_ctg


def get_items():
    all_annotations_id = []
    all_annotations_doc = []
    with open(path + 'annotation_vectors.csv') as annotation_vectors:
        reader = csv.reader(annotation_vectors, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        last_id = 0
        this_id_list = []
        for item in reader:
            this_id = int(item[0])
            if last_id == this_id:
                this_id_list.append([int(item[0]), item[1], time.strptime(item[2], "%Y-%m-%d")])
            else:
                all_annotations_id.append(this_id_list)
                last_id = this_id
                this_id_list = []
                this_id_list.append([int(item[0]), item[1], time.strptime(item[2], "%Y-%m-%d")])
            all_annotations_doc.append([item[1], int(item[0]), time.strptime(item[2], "%Y-%m-%d")])
    return all_annotations_id[1:], sorted(all_annotations_doc[1:], key=lambda docid: docid[0])


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
    for ids in all_annotations_id:
        if i % 100 == 0:
            print "progress: " + str(i) + ", " + str(len(all_annotations_id)) + ", " + str(
                (i * 100) / float(1.0 * len(all_annotations_id))) + "%"
            if i != 0: break
        i += 1
        vector = {}
        indeces = []
        for item in ids:
            docid = item[1]
            for doc in all_annotations_doc:
                if doc[0][0] == docid:
                    for doc_w_docid in doc:
                        dtime = datetime(*doc[0][2][:6]).isoformat()[:10]
                        if doc_w_docid[1] in vector.keys():
                            vector[str(doc_w_docid[1]) + '_' + dtime] = vector[doc_w_docid[1]] + 1
                        else:
                            vector[str(doc_w_docid[1]) + '_' + dtime] = 1
                    break
        for k, v in vector.iteritems():
            indeces.append([k, v])
        all_d_vector.append([int(ids[0][0]), indeces])
    return all_d_vector


def main():
    print "Loading Items"
    all_annotations_id, all_annotations_doc = get_items()
    all_annotations_doc = doc_mapping(all_annotations_doc)
    print "Building Distributions"
    all_d_vecs_time = build_vectors(all_annotations_id, all_annotations_doc)
    with open('all_distributions_time.csv', 'wb') as out_file:
        writer = csv.writer(out_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for line in all_d_vecs_time:
            tmp = list(chain.from_iterable(line[1]))
            writer.writerow([line[0]] + tmp)


if __name__ == "__main__":
    main()

