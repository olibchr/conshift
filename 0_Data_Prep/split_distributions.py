import csv, sys, sqlite3

path = sys.argv[1]
article_map = {}
DM = []
WP = []
NYT = []
IND = []
HP = []


def get_items():
    all_annotations = []
    with open(path + 'all_annotation_vectors.csv') as annotation_vectors:
        reader = csv.reader(annotation_vectors, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for item in reader:
            all_annotations.append(item)
    return all_annotations

def get_articles():
    article_map = {}
    conn = sqlite3.connect(path + 'articles.db')
    c = conn.cursor()
    for a in c.execute("SELECT id,publisher FROM articles"):
        article_map[a[0]] = a[1]
    return article_map


def main():
    all_annotations = get_items()
    article_map = get_articles()
    for annot in all_annotations:
        a_id = annot[1]
        if article_map[a_id] == 'Daily Mail':
            DM.append(annot)
        elif article_map[a_id] == 'The huffington Post':
            HP.append(annot)
        elif article_map[a_id] == 'The Independent':
            IND.append(annot)
        elif article_map[a_id] == 'New York Times':
            NYT.append(annot)
        elif article_map[a_id] == 'The Washington Post':
            WP.append(annot)
        else:
            print 'error with: ' + a_id

    with open('DM_annotation_vectors.csv', 'wb') as DM_out:
        writer = csv.writer(DM_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for a_vec in DM:
            writer.writerow(a_vec)
    with open('WP_annotation_vectors.csv', 'wb') as WP_out:
        writer = csv.writer(WP_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for a_vec in WP:
            writer.writerow(a_vec)
    with open('HP_annotation_vectors.csv', 'wb') as HP_out:
        writer = csv.writer(HP_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for a_vec in HP:
            writer.writerow(a_vec)
    with open('NYT_annotation_vectors.csv', 'wb') as NYT_out:
        writer = csv.writer(NYT_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for a_vec in NYT:
            writer.writerow(a_vec)
    with open('IND_annotation_vectors.csv', 'wb') as IND_out:
        writer = csv.writer(IND_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for a_vec in IND:
            writer.writerow(a_vec)


if __name__ == "__main__":
    main()