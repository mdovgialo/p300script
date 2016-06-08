from obci.interfaces.bci.p300_MD.helper_functions import get_epochs_fromfile, evoked_from_smart_tags, evoked_pair_plot_smart_tags 
import sys
import os.path
import os
import numpy as np
import json
#settings:
baseline = -0.1
filtr = [[1, 30], [0.1, 33], 3, 12]
#~ montage = ['custom', 'M1', 'M2']
#~ montage = ['custom', 'A1', 'A2']
montage = ['custom', 'Cz']
#~ montage = ['csa']


target = sys.argv[1]
#name of target tag name
work_type = sys.argv[2]
files = sys.argv[3:]
#provide it raws

if work_type == 'visual':
    def target_tags_func(tag):
        if tag['name'] == target:
            return True
        return False
    def nontarget_tags_func(tag):
        if tag['name'] != target:
            return True
        return False
elif work_type == 'visualsek':
    def target_tags_func(tag):
        if tag['description']['name'] == target:
            return True
        return False
    def nontarget_tags_func(tag):
        if tag['description']['name'] != target:
            return True
        return False
        
elif work_type == 'target':
    def target_tags_func(tag):
        if tag['desc']['index'] == target:
            return True
    def nontarget_tags_func(tag):
        if tag['desc']['index'] != target:
            return True
        return False
    
        
def prepare_for_tester(tg, ntg, dir, name, baseline, montage):
    eq = min(k.shape[2] for k in [i.get_samples()[None,:,:] for i in tg]+[i.get_samples()[None,:,:] for i in ntg])-1
    targets = np.concatenate([i.get_samples()[None,:,:eq] for i in tg], axis = 0)
    nontargets = np.concatenate([i.get_samples()[None,:,:eq] for i in ntg], axis = 0)
    targets_mean = targets.mean(axis=2)[:,:,None]
    nontargets_mean = nontargets.mean(axis=2)[:,:,None]
    
    
    meta = {}
    meta['channels_names'] = tg[0].get_param('channels_names')
    meta['sampling_rate'] = float(tg[0].get_param('sampling_frequency'))
    meta['baseline'] = baseline
    meta['channel_gains'] =  tg[0].get_param('channels_gains')
    
    with open(os.path.join(dir, name+'_m_{}_meta.json'.format(montage)), 'w') as datafile:
        json.dump(meta, datafile)
    np.save(os.path.join(dir, name+'_m_{}_targets.npy'.format(montage)), targets-targets_mean)
    np.save(os.path.join(dir, name+'_m_{}_nontargets.npy'.format(montage)), nontargets-nontargets_mean,)

for path in files:
    dirname, filename = os.path.split(path)
    datasetname, ext = os.path.splitext(filename)
    ds = os.path.join(dirname, datasetname)
    outputpath = os.path.join(dirname, 'output')
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)
    
    target_tags, nontarget_tags = get_epochs_fromfile(ds, start_offset=baseline,duration=1.0, 
                        filter=filtr, montage=montage,
                        drop_chnls = [ u'AmpSaw', u'DriverSaw', u'trig1', u'trig2'],
                        target_tags_func = target_tags_func,
                        nontarget_tags_func = nontarget_tags_func,
                        tag_name = None)
                        
    
    if len(target_tags)==0:
        raise Exception('Extracted 0 epochs, check your target tag name')
    chnames = target_tags[0].get_param('channels_names')
    check_first_list = list(range(1, len(target_tags), 5))
    check_first_list = [5, 10, 20, 40,]
    check_first_list.append(-1)
    for i in check_first_list:
        fig = evoked_pair_plot_smart_tags(target_tags[:i], nontarget_tags[:i],
                                        chnames, show=False)
        fig.set_size_inches(18.5, 30.5, forward=True)
        fig.tight_layout()
        fig.savefig(os.path.join(outputpath, datasetname+'_{:02d}_{}_rs.png'.format(i, montage)), dpi=150)
    prepare_for_tester(target_tags, nontarget_tags, outputpath, datasetname, baseline, montage)

