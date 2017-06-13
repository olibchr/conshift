import csv
path =  '/Users/oliverbecher/1_data/0_cwi/1_data/'

def load_distr():
    with open(path + 'all_distributions_time.csv') as distr_vec:
        reader = csv.reader(distr_vec, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        all_data = []
        for row in reader:
            articles = set([art.split('_')[1] for art in row[1:]])
            all_data.append([int(row[0]),len(articles)])
    return all_data


def get_ctg():
    all_id_to_ctg = {}
    with open(path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_id_to_ctg[int(row[1])] = row[0]
    return all_id_to_ctg


def save_ind_cnt(out):
    with open('index_cnt_update.csv','w') as outfile:
        writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for o in out:
            writer.writerow([all_id_to_ctg[o[0]], o[0], o[1]])

concept_counts = load_distr()
all_id_to_ctg= get_ctg()
save_ind_cnt(concept_counts)