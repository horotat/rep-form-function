import json
import csv
import logging
import imaginet.data_provider as dp
import imaginet.defn.lm_visual_vanilla as D
from scipy.spatial.distance import cosine
import imaginet.task
import numpy

root = '/home/gchrupal/cl-resubmit/'
data_path = '/home/gchrupal/cl-resubmit/data/'
#model_im_path = root + "/run-lm_visual_vanilla-1/model.r.e7.zip"
#model_lm_path = root + "/run-lm-0/model.r.e6.zip"
#model_sum_path = root + "/run-vectorsum-0/model.r.e7.zip"
model_im_path = root + "models/imaginet.zip"
model_lm_path = root + "models/lm.zip"
model_sum_path = root + "models/sum.zip"

def dump_activations(sent, models):
    for name, model, task in models:
        logging.info("Writing activations for {}".format(name))
        states = imaginet.task.states(model, sent, task=task)
        numpy.save(data_path + "states_{}.npy".format(name), states)

def main():
    logging.getLogger().setLevel('INFO')
    logging.info("Loading data")
    prov = dp.getDataProvider(dataset='coco', root=root, audio_kind=None)
    sent = list(prov.iterSentences(split='val'))
    sent_id = [ sent_i['sentid'] for sent_i in sent]
    sent_tok = [ sent_i['tokens'] for sent_i in sent]
    logging.info("Loading imaginet model")
    model_im = D.load(model_im_path)
    logging.info("Loading plain LM model")
    model_lm = imaginet.task.load(model_lm_path)
    logging.info("Loading vectorsum model")
    model_sum = imaginet.task.load(model_sum_path)
    dump_activations([sent_i['tokens'] for sent_i in sent ],
                           [("visual", model_im, model_im.visual ),
                            ("textual", model_im, model_im.lm),
                            ("lm", model_lm, model_lm.task),
                            ("sum", model_sum, model_sum.task)])
    writer = csv.writer(open(data_path + '/omission_coco_val.csv',"w"))
    writer.writerow(["sentid", "position", "word",
                     "omission_v",
                     "omission_t",
                     "omission_lm",
                     "omission_sum"])
    for i in  range(len(sent)):
        logging.info("Processing: {}".format(sent_id[i]))
        O_v = omission(model_im, sent_tok[i], task=model_im.visual)
        O_t = omission(model_im, sent_tok[i], task=model_im.lm)
        O_lm = omission(model_lm, sent_tok[i], task=model_lm.task)
        O_sum = omission(model_sum, sent_tok[i], task=model_sum.task)
        for j in range(len(sent_tok[i])):
            writer.writerow([sent_id[i],
                            j,
                            sent_tok[i][j],
                            O_v[j],
                            O_t[j],
                            O_lm[j],
                            O_sum[j]])

def omission(model, toks, task=None):
    if task is None:
        task = model.visual
    orig = imaginet.task.states(model, [toks], task=task)[0]
    omit = imaginet.task.states(model,
                      [ toks[:i] + toks[i+1:] for i in range(len(toks))],
                      task=task)
    return [ cosine(orig[-1], omit_i[-1]) for omit_i in omit]



if __name__ == '__main__':
    main()
