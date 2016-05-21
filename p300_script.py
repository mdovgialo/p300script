from obci.interfaces.bci.p300_MD.helper_functions import get_epochs_fromfile, evoked_from_smart_tags, evoked_pair_plot_smart_tags 
import sys
import os.path
import os
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
        
def prepare_for_tester(tg, ntg, dir):
    targets = np.array([i.get_samples() for i in tg])
    nontargets = np.array([i.get_samples() for i in ntg])
    targets_mean = targets.mean(axis=2)[:,:,None]
    nontargets_mean = nontargets.mean(axis=2)[:,:,None]
    
    
    meta = {}
    meta['channels_names'] = tg[0].get_param('channels_names')
    meta['sampling_rate'] = float(tg[0].get_param('sampling_frequency'))
    meta['baseline'] = baseline
    meta['channel_gains'] =  tg[0].get_param('channels_gains')
    
    with open(os.path.join(dir, 'meta.json'), 'w') as datafile:
        json.dump(meta, datafile)
    np.save(os.path.join(dir, 'targets.npy'), targets-targets_mean)
    np.save(os.path.join(dir, 'nontargets.npy'), nontargets[1:-2]-nontargets_mean[1:-2],)

for path in files:
    dirname, filename = os.path.split(path)
    datasetname, ext = os.path.splitext(filename)
    ds = os.path.join(dirname, datasetname)
    outputpath = os.path.join(dirname, 'output')
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)
    filtr = [[1, 30], [0.1, 33], 3, 12]
    montage = ['custom', 'M1', 'M2']
    montage = ['custom', u'Cz']
    target_tags, nontarget_tags = get_epochs_fromfile(ds, start_offset=-0.1,duration=1.0, 
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
    prepare_for_tester(target_tags, nontarget_tags, outputpath)

