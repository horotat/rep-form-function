import pandas as pd
import numpy as np
import imaginet.data_provider as dp
from scipy.stats.mstats import mquantiles
from sklearn.metrics import mutual_info_score
import csv
import logging

def ngram(seq, order):
    pad = ['*--*']*(order-1)+seq
    return [ ' '.join(tup) for tup in zip(*[pad[i:] for i in range(order)]) ]


def quantize(v):
    return np.digitize(v, mquantiles(v, prob=np.linspace(0,1,20)))

def main():
    logging.getLogger().setLevel('INFO')
    logging.info("Loading input data")
    root = '/home/gchrupal/reimaginet/'
    prov = dp.getDataProvider(dataset='coco', root=root, audio_kind=None)
    ids = np.array([senti['sentid'] for senti in prov.iterSentences(split='val')])
    data = pd.read_csv("/home/gchrupal/cl-resubmit/data/depparse_coco_val.csv")
    sent_data = dict(senti for senti in data.groupby(['sentid']))
    with open("/home/gchrupal/cl-resubmit/data/mutual_examples.csv", "w") as out_ex:
        writer_ex = csv.writer(out_ex)
        writer_ex.writerow(["pathway", "condition", "order", "dimension", "index","history","history_w"])
        with open("/home/gchrupal/cl-resubmit/data/mutual.csv", "w") as out:
            writer = csv.writer(out)
            writer.writerow(["pathway", "condition", "order", "dimension", "mi"])
            for net in ["visual", "textual", "lm", "sum"]:
                states = np.load("/home/gchrupal/cl-resubmit/data/states_{}.npy".format(net), encoding='bytes')
                S = quantize(np.vstack([state[:-1,:] for state in states]).T)
                for typ in ['word', 'dep']:
                    for order in [1,2,3]:
                        logging.info("Computing scores for {}:{}:{}".format(net, typ, order))
                        context_w = [item for i in ids for item in ngram(list(sent_data[i]['word']), order) ]
                        context = [item for i in ids for item in ngram(list(sent_data[i][typ]), order) ]
                        mi = []
                        for i in range(1024):
                            mi.append(mutual_info_score(S[i], context))
                            writer.writerow([net, typ, order, i, mi[-1]])
                        logging.info("Finding examples for  {}:{}:{}".format(net, typ, order))
                        top3 = np.array(mi).argsort()[-3:]
                        for dim in top3:
                            for index in S[dim].argsort()[-10:]:
                                writer_ex.writerow([net, typ, order, dim, index, context[index], context_w[index]])



if __name__ == '__main__':
    main()
