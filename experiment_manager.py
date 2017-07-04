import wiki_comparison
import csv, sys, random
from joblib import Parallel, delayed
import multiprocessing


#path = '/Users/oliverbecher/1_data/0_cwi/1_data/'
path = '/export/scratch1/home/becher/data/'
conceptsPerRequest = 30

num_concepts = int(sys.argv[2])
num_cores = multiprocessing.cpu_count()
num_jobs = num_cores * 3/4
filter_pre_selec = [3678, 49790, 30203, 19748, 54047, 62201, 5479, 54212, 60247, 12411, 71096, 12817, 70736, 28092, 64488, 26417, 11541, 20049, 6456, 51595, 8333, 71203, 45977, 49186, 16230, 56332, 39790, 24747, 50234, 67207, 70984, 49595, 59927, 27122, 25026, 57512, 19566, 8128, 65555, 55475, 8991, 62169, 11314, 44264, 25506, 55447, 64554, 28425, 15401, 62961, 11890, 481, 59589, 23647, 42452, 7194, 49875, 58015, 68676, 43742, 44071, 28073, 60068, 31694, 40382, 1182, 17367, 55301, 60950, 59329, 26335, 68560, 565, 32923, 2002, 58763, 33409, 44990, 61504, 25765, 22053, 34594, 875, 22080, 30000, 55099, 53599, 18847, 20470, 62974, 20784, 55624, 16476, 28786, 14310, 47358, 24598, 51456, 56263, 63090, 67789, 39876, 35213, 7913, 21358, 14638, 55005, 15453, 32599, 69587, 70863, 36620, 12366, 6015, 61761, 60503, 58818, 1808, 35935, 56701, 20606, 45232, 34216, 58353, 35924, 55760, 34913, 49299, 23006, 37297, 57414, 28317, 14639, 42375, 26096, 61005, 62064, 5705, 15335, 66282, 43844, 10066, 39316, 51414, 53327, 36548, 9564, 65403, 30966, 3643, 22407, 21798, 68095, 8360, 53288, 63299, 32711, 70758, 10975, 27210, 39808, 40687, 46040, 2805, 66863, 54754, 15639, 13291, 5586, 29526, 43042, 66341, 3185, 21904, 28880, 50488, 8923, 26969, 4057, 62361, 25184, 7904, 9521, 7582, 25397, 30728, 21672, 16882, 65167, 45870, 29732, 25505, 1914, 29269, 68257, 4991, 20346, 38029, 29873, 12126, 48774, 67507, 2174, 36446, 58999, 432, 36619, 65760, 68091, 71094, 39694, 45427, 39769, 43001, 69338, 28746, 47260, 16394, 50656, 23364, 48657, 36610, 30935, 11454, 13501, 8500, 3875, 49191, 16914, 5821, 46682, 17644, 34697, 35986, 70584, 682, 60592, 27285, 36935, 44772, 54817, 6845, 31262, 1009, 38739, 28347, 40628, 9953, 39897, 70063, 11086, 27490, 51382, 8021, 19306, 19999, 16915, 42810, 43271, 17581, 64066, 4097, 16292, 26418, 69898, 14800, 12319, 53178, 11134, 38228, 32695, 7059, 34181, 68536, 4924, 62097, 30301, 29371, 64990, 40075, 64350, 66926, 26980, 19235, 17145, 66825, 35562, 41798, 34860, 59719, 61777, 40872, 34076, 52451, 11678, 54273, 2969, 5583, 17787, 53949, 61105, 42971, 44686, 65255, 17935, 38833, 71120, 29278, 40387, 8444, 22058, 43762, 20847, 53754, 6025, 34719, 45380, 35668, 47092, 67975, 38506, 28163, 61178, 19991, 42686, 51351, 38388, 51340, 57703, 55444, 68974, 64729, 17905, 36574, 11508, 107, 17403, 5077, 27837, 59132, 44131, 16920, 169, 16491, 17111, 8515, 49861, 16027, 40553, 70298, 26906, 42353, 5256, 68995, 5169, 46686, 19596, 33659, 23653, 41597, 46295, 37904, 61116, 66343, 22531, 9158, 28889, 32077, 71440, 42041, 68206, 44852, 71432, 70851, 15839, 28273, 25209, 68324, 15777, 62537, 6973, 12531, 64054, 30433, 7291, 12146, 29462, 37884, 35484, 58844, 14699, 19713, 16840, 58754, 13032, 60199, 31890, 48352, 25115, 52383, 51577, 58624, 43589, 50472, 6446, 52290, 25269, 2865, 9621, 27742, 26706, 21234, 15237, 67961, 7175, 22539, 24911, 63524, 31028, 44937, 22940, 4925, 56520, 65137, 616, 45234, 43666, 17973, 37161, 35198, 36096, 58181, 63105, 15748, 11050, 12393, 11715, 34731, 12614, 63387, 47579, 8214, 15754, 59010, 53222, 40309, 31398, 19669, 58000, 13609, 64070, 45046, 69118, 55580, 36957, 9732, 66073, 24521, 64025, 6058, 40800, 53954, 31840, 30388, 70651, 62029, 12524, 50005, 36239, 58171, 44760, 6945, 3002, 13966, 19391, 56861, 60273, 57153, 957, 40074, 46642, 8127, 29256, 2764, 70969, 12909, 57849, 41445, 69384, 27885, 24787, 57928, 70565, 51271, 45961, 33826, 32708, 3921, 45996, 45613, 31285, 47934, 38593, 62634, 54657, 28088, 53729, 11119, 47435, 56274, 60067, 36802, 27064, 17761, 31628, 41096, 53145, 5520, 23689, 5295, 15596, 46786, 68487, 41280, 31257, 51905, 4179, 4644, 14192, 43350, 31472, 62542, 35169, 15119, 33551, 59170, 24696, 38341, 50908, 25845, 54088, 68409, 57299, 10290, 70942, 51711, 28694, 14423, 63660, 66342, 43905, 25710, 38875, 54423, 18939, 25757, 69570, 50227, 45696, 45229, 42942, 39738, 37158, 59124, 18387, 63996, 39767, 65781, 34105, 26398, 41034, 36654, 30139, 12076, 29892, 18369, 61376, 25660, 15352, 50360, 1175, 8886, 29554, 33450, 37758, 19510, 57019, 18202, 47218, 13660, 65393, 71254, 17284, 70615, 69884, 7305, 48244, 50558, 14132, 60360, 69031, 67128, 36317, 1212, 24677, 35878, 32754, 65094, 30585, 49149, 37253, 59123, 60174, 1959, 5198, 54456, 12362, 59656, 64397, 64487, 864, 10725, 10518, 7795, 51696, 14940, 35358, 18543, 18497, 61440, 59914, 55158, 8745, 42523, 64431, 55693, 39850, 55211, 2379, 29436, 1142, 56989, 8015, 4283, 63614, 21671, 17482, 8507, 29639, 10264, 14571, 60321, 39171, 15686, 45252, 40690, 31510, 64863, 12905, 61487, 34834, 36147, 22904, 17695, 62168, 14920, 46500, 63325, 62409, 9819, 66821, 32870, 49089, 39089, 15447, 26225, 67111, 26181, 68882, 9977, 61486, 50421, 6792, 40699, 45531, 10003, 36776, 2280, 59683, 67705, 68724, 57733, 3339, 35977, 18248, 52754, 38344, 66199, 11203, 31010, 48530, 60561, 20911, 44846, 3533, 70899, 67303, 8331, 80, 68411, 6574, 44305, 18646, 3514, 48248, 56534, 35887, 3360, 19636, 27680, 17234, 62642, 59415, 27060, 44923, 16552, 54920, 68469, 70727, 8866, 33771, 22241, 24391, 11140, 13988, 31797, 10755, 59964, 64606, 17682, 14448, 63460, 34823, 41141, 34028, 68072, 3939, 28941, 14012, 20643, 29880, 57855, 41488, 43451, 62385, 35481, 53075, 67644, 21499, 47423, 28697, 50140, 29434, 3619, 12758, 11903, 1693, 31404, 38317, 10953, 39621, 30329, 41465, 57352, 27082, 30776, 54519, 27937, 8471, 36389, 44526, 56807, 6863, 19544, 21015, 12143, 51283, 16310, 47147, 65721, 68264, 62594, 61386, 52056, 21855, 38043, 38395, 34278, 51404, 26957, 3447, 64764, 64346, 37972, 20327, 2917, 53740, 16121, 47725, 48805, 34402, 8292, 30913, 41110, 20737, 25033, 6064, 49044, 40073, 51300, 69163, 14716, 16424, 15872, 16144, 12363, 17016, 10279, 58231, 21745, 57458, 9018, 64595, 33221, 68548, 13390, 26526, 15055, 37098, 53230, 2428, 37052, 38142, 24748, 26308, 38572, 10065, 21121, 36807, 43534, 51242, 51946, 61128, 45471, 14259, 59194, 61939, 21237, 2383, 42805, 40558, 38329, 60787, 58096, 2042, 49015, 12702, 21385, 31708, 21093, 66045, 48192, 69987, 15481, 40128, 13918, 20342, 57954, 24366, 56511, 11078, 44541, 14791, 48724, 42126, 62963, 40437, 37513, 20079, 53209, 33718, 4840, 70190, 41464, 55566, 61423, 41525, 51075, 55796, 13707, 68874, 124, 67058, 18372, 40469, 62563, 70266, 7080, 9957, 33794, 20205, 30785, 4656, 44712, 26694, 52522, 66724, 56548, 48730, 44135, 38596, 12697, 61359, 7815, 60442, 47691, 66788, 16963, 16338, 2610, 43437, 35230, 7432, 2170, 47244, 71287, 20865, 60002, 1979, 9414, 43071, 42079, 15878, 12134, 71516, 17193, 60081, 50673, 39913, 60773, 45183, 47386, 53469, 13143, 12386, 51700, 46113, 56712, 18396, 52846, 15103, 26009, 33825, 39335, 15938, 19444, 22807, 26648, 68048, 9656, 50100, 25252, 17582, 13680, 7262, 23434, 4816, 20900, 10851, 1548, 14695, 31430, 48911, 15316, 60804, 20050, 14135, 41053, 5942, 32019]


def get_ind_cnt():
    all_ind = []
    all_ind_dt = dict()
    with open(path + 'index_cnt_no_ctg.csv') as ind_cnt:
        reader = csv.reader(ind_cnt, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_ind.append([row[0], int(row[1]), int(row[2])])
            all_ind_dt[int(row[1])] = int(row[2])
    return all_ind, all_ind_dt


# !!!offset 3 on change!!!
def get_ranges(ind_cnt):
    offset1 = 0
    offset2 = 0
    offset3 = 0
    for item in ind_cnt:
        if item[2] > 500: offset1 += 1 # tbd
        if item[2] > 200: offset2 += 1
        if item[2] > 99: offset3 += 1 # tbd
        else: break
    print offset1, offset2, offset3
    return offset1, offset2, offset3


def stratefied_sample(offset1, offset2, offset3):
    if num_concepts/3 > offset1: top_cnt = random.sample(xrange(num_concepts / 3), num_concepts / 3)
    else:
        top_cnt = random.sample(xrange(offset1), num_concepts / 3)
    if num_concepts/3 > offset2: med_cnt = random.sample(xrange(num_concepts / 3), num_concepts / 3)
    else:
        med_cnt = random.sample(xrange(offset1, offset2), num_concepts / 3)
    low_cnt = random.sample(xrange(offset2, offset3), num_concepts / 3)
    all_indeces = top_cnt + med_cnt + low_cnt
    return all_indeces


def get_filter_badges():
    if num_concepts == 990: return [filter_pre_selec[i:i+conceptsPerRequest] for i in range(0,len(filter_pre_selec), conceptsPerRequest)]
    all_ind_cnt, all_ind_dt = get_ind_cnt()
    offset1, offset2, offset3 = get_ranges(all_ind_cnt)
    filter_indeces = stratefied_sample(offset1, offset2, offset3)
    filters = [all_ind_cnt[i][1] for i in filter_indeces]
    return [filters[i:i+conceptsPerRequest] for i in range(0,len(filters), conceptsPerRequest)]


def filter_badges_24():
    if num_concepts == 990: return [filter_pre_selec[i:i+conceptsPerRequest] for i in range(0,len(filter_pre_selec), conceptsPerRequest)]
    all_ind_cnt, all_ind_dt = get_ind_cnt()
    with open(path + 'filter_subset', 'r') as in_file:
        subset = map(int, in_file.read().split(', '))
    for f in subset:
        if all_ind_dt[f] < 24: subset.pop(subset.index(f))
    rand_smpl = [ subset[i] for i in sorted(random.sample(xrange(len(subset)), num_concepts)) ]
    return [rand_smpl[i:i+conceptsPerRequest] for i in range(0,len(rand_smpl), conceptsPerRequest)]


def exp1():
    print 'Experiment 1'
    filter_badges = get_filter_badges()
    print filter_badges
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_1)(badge, path, 24) for badge in filter_badges)
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_1)(badge, path, 12) for badge in filter_badges)
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_1)(badge, path, 6) for badge in filter_badges)
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_1)(badge, path, 4) for badge in filter_badges)


def exp2():
    filter_badges = get_filter_badges()
    print 'Experiment 2'
    print filter_badges
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_2)(badge, path, 24) for badge in filter_badges)
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_2)(badge, path, 12) for badge in filter_badges)
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_2)(badge, path, 6) for badge in filter_badges)
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_2)(badge, path, 4) for badge in filter_badges)


def exp3():
    filter_badges = get_filter_badges()
    print 'Experiment 3'
    print filter_badges
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_3)(badge, path, 24) for badge in filter_badges)
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_3)(badge, path, 12) for badge in filter_badges)
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_3)(badge, path, 6) for badge in filter_badges)
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_3)(badge, path, 4) for badge in filter_badges)


def exp4():
    filter_badges = filter_badges_24()
    print 'Experiment 4'
    print filter_badges
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_4)(badge, path, 24) for badge in filter_badges)
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_4)(badge, path, 12) for badge in filter_badges)
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_4)(badge, path, 6) for badge in filter_badges)
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_4)(badge, path, 4) for badge in filter_badges)


def exp5():
    filter_badges = get_filter_badges()
    print 'Experiment 5'
    print filter_badges
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_1)(badge, path, 100) for badge in filter_badges)
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_2)(badge, path, 100) for badge in filter_badges)
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_3)(badge, path, 100) for badge in filter_badges)
    Parallel(n_jobs=num_jobs)(delayed(wiki_comparison.experiment_4)(badge, path, 100) for badge in filter_badges)



if sys.argv[1] == '1':
    exp1()
if sys.argv[1] == '2':
    exp2()
if sys.argv[1] == '3':
    exp3()
if sys.argv[1] == '4':
    exp4()
if sys.argv[1] == '5':
    exp5()