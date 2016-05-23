import sys
import os.path
import os
import numpy as np
import json
import pylab as pb
#you can plot combinations of plots using this script
#it uses .npy files exported by p300 script
#you should provide original .raw files path

montage = sys.argv[1]
files = sys.argv[2:]

targets = []
nontargets = []
labels = []

def plot(targets, nontargets, meta, labels):
    chnames = meta['channels_names']
    Fs = meta['sampling_rate']
    baseline = meta['baseline']
    time = np.linspace(0+baseline, targets[0].shape[2]/Fs+baseline, targets[0].shape[2])
    fig = pb.figure()
    
    for nr, i in enumerate(chnames):
        legend_handles = []
        legend_labels = []
        ax = fig.add_subplot( (len(chnames)+1)/2, 2, nr+1)
        for label, target, nontarget in zip(labels, targets, nontargets):
            evt = target.mean(axis=0)*float(meta['channel_gains'][nr])
            evnt = nontarget.mean(axis=0)*float(meta['channel_gains'][nr])
            line1, = ax.plot(time, evt[nr],)
            line2, = ax.plot(time, evnt[nr], color = 'gray', alpha=0.4,)
            ax.grid(True, 'both')
            legend_handles.append(line1)
            legend_handles.append(line2)
            legend_labels.append('{} targets N:{}'.format(label, len(target)))
            legend_labels.append('{} nontargets N:{}'.format(label, len(nontarget)))
            
            
            ax.set_title(i)
    
    fig.legend(legend_handles, legend_labels, 'lower right')
    return fig

for f in files:
    dirname, filename = os.path.split(f)
    datasetname, ext = os.path.splitext(filename)
    ds = os.path.join(dirname, datasetname)
    outputpath = os.path.join(dirname, 'output')
    labels.append(' '.join(datasetname.split('_')[0:5]))
    target_filename = datasetname+'_m_{}_targets.npy'.format(montage)
    nontarget_filename = datasetname+'_m_{}_nontargets.npy'.format(montage)
    meta_filename = datasetname+'_m_{}_meta.json'.format(montage)
    targets.append(np.load(os.path.join(outputpath, target_filename)))
    nontargets.append(np.load(os.path.join(outputpath, nontarget_filename)))
    meta = json.load(open((os.path.join(outputpath, meta_filename))))

fig = plot(targets, nontargets, meta, labels)
fig.set_size_inches(18.5, 30.5, forward=True)
fig.tight_layout()
fig.savefig(os.path.join(outputpath, 'combination_{}.png'.format(montage)), dpi=150)

    
