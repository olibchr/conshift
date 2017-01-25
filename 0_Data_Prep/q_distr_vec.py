import csv, operator
import sys, time, string
from sklearn.feature_extraction.text import TfidfTransformer
from scipy.sparse import lil_matrix
from sklearn.preprocessing import normalize

"""
This program calculates density distributions for all annotations and saves those as sparse vectors
"""
if len(sys.argv) < 2:
    print "Give dir path to annotion files!"
    exit()
path = sys.argv[1]
quarters = [time.strptime("2014-11-13", "%Y-%m-%d"), time.strptime("2015-02-13", "%Y-%m-%d"), time.strptime("2015-05-13", "%Y-%m-%d"), time.strptime("2015-08-13", "%Y-%m-%d")]


def get_ctg():
    all_id_to_ctg = {}
    with open(path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_id_to_ctg[int(row[1])] = row[0]
    return all_id_to_ctg, all_id_to_ctg


def get_items():
    all_annotations = []
    with open(path + 'annotation_vectors.csv') as annotation_vectors:
        reader = csv.reader(annotation_vectors, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        i = 0
        for item in reader:
            i += 1
            if i > 1000:
                break
            annots = item[2][1:-1].split(',')
            annots = [x.strip(' ') for x in annots]
            r_annots = []
            for an in annots:
                if an == '-1':
                    continue
                r_annots.append(an)
            #annots = [x.replace('-1','') for x in annots]
            this_q = 0
            this_release = time.strptime(item[1], "%Y-%m-%d")
            if this_release <= quarters[0]:
                this_q = 1
            elif this_release <= quarters[1]:
                this_q = 2
            elif this_release <= quarters[2]:
                this_q = 3
            elif this_release <= quarters[3]:
                this_q = 4
            all_annotations.append([item[0], this_q, r_annots])
    return sorted(all_annotations, key=lambda all_annotation: all_annotations[1])


def split_set(all_items):
    q1 = []
    q2 = []
    q3 = []
    q4 = []
    for item in all_items:
        if item[1] == 1:
            q1.append(item)
        elif item[1] == 2:
            q2.append(item)
        elif item[1] == 3:
            q3.append(item)
        elif item[1] == 4:
            q4.append(item)
    return [q1,q2,q3,q4]


def invert_items(all_items, filter, all_id_to_ctg, i):
    index_cnt = {key: 0 for key in filter}
    inverted_items = []
    for item in all_items:
        for annot in item[2]:
            if annot == '':
                continue
            annot = int(annot)
            inverted_items.append([annot, item])
            index_cnt[annot] = index_cnt[annot] + 1
    with open('q' + str(i) + '_index_cnt.csv', 'wb') as cnt_out:
        writer = csv.writer(cnt_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        sorted_index_cnt = sorted(index_cnt.items(), key=operator.itemgetter(1), reverse=True)
        for key in sorted_index_cnt:
            if "Category" in all_id_to_ctg[key[0]]:
                continue
            writer.writerow([all_id_to_ctg[key[0]], key[0], key[1]])
    sorted(inverted_items, key=lambda key: inverted_items[0])
    return inverted_items


def build_vectors(inverted_items, filters):
    all_d_vector = []
    i = 0
    for filter in filters:
        if i % 500 == 0:
            print "progress: " + str(i) + ", " + str(len(filters)) + ", " + str(
                (i * 100) / float(1.0 * len(filters))) + "%"
        i += 1
        vector = {}
        indeces = []
        for item in inverted_items:
            if item[0] == filter:
                for annot in item[1][2]:
                    if annot in vector.keys():
                        vector[annot] = vector[annot] + 1
                    else:
                        vector[annot] = 1
                item[0] = None

        for k, v in vector.iteritems():
            indeces.append([k, v])
        all_d_vector.append([int(filter), indeces])
    return all_d_vector


def build_sparse(all_d_content, lilx, lily):
    positions = []
    data = []
    for distr in all_d_content:
        this_position = []
        this_data = []
        for tuple in distr[1]:
            if tuple[0] == '' or tuple[1] == '':
                continue
            this_position.append(tuple[0])
            this_data.append(tuple[1])
        positions.append(this_position)
        data.append(this_data)
    sparse_entities = lil_matrix((lilx, lily))
    sparse_entities.rows = positions
    sparse_entities.data = data
    sparse_entities.tocsr()
    return sparse_entities


def build_all_idf(all_d_vec):
    transformer = TfidfTransformer(smooth_idf=False)
    sparse_entities = transformer.fit_transform(all_d_vec)
    return sparse_entities


def revert(sparse_entities):
    all_distributions = []
    sparse_entities = sparse_entities.tolil()
    for i in range(0,sparse_entities.shape[0]):
        this_row = sparse_entities.getrow(i)
        this_features = []
        for offset in range(0,len(this_row.data[0])):
            this_features.append((this_row.rows[0][offset], this_row.data[0][offset]))
        all_distributions.append((i,this_features))
    return all_distributions


def main():
    filter_id_to_ctg, all_id_to_ctg = get_ctg()

    filters = [x for x in all_id_to_ctg.keys()]

    print "Loading data.. "

    print "Annotations: " + str(len(all_id_to_ctg))

    all_items = get_items()

    print "Articles: " + str(len(all_items))

    q_items = split_set(all_items)

    print len(q_items)
    i = 1
    for qtr_items in q_items:
        print "Quarter " + str(i) + ": " + str(len(qtr_items)) + " items."
        inverted_items = invert_items(qtr_items, filters, all_id_to_ctg, i)

        print "Annotations: " + str(len(inverted_items))
        q_distributions = build_vectors(inverted_items, filters)

        print "Successfully built "
        q_distributions = build_sparse(q_distributions, len(q_distributions), len(all_id_to_ctg))
        print "test1"
        w_q_distr = build_all_idf(q_distributions)
        print "test2"
        w_q_distr = revert(w_q_distr)
        print "test3"
        with open('q' + str(i) + '_distributions.csv', 'wb') as out_file:
            writer = csv.writer(out_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for line in w_q_distr:
                writer.writerow(line)
        i+=1
        print "q done"


if __name__ == "__main__":
    main()
