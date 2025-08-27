"""
# Author: Yuhan Fei & Jiasheng Zhang
# Created Time :  15 May 2021
# Revised Time v0:  12 May 2023
# Revised Time v1:  22 Feb 2024
# Revised Time v2:  29 May 2024
"""

import pandas as pd
import numpy as np 
import os
from scipy.signal import savgol_filter
from PIL import Image
import matplotlib as mpl
import matplotlib.pyplot as plt

import matplotlib.gridspec as gridspec
ACGU_PATH = os.path.join('/content/drive/MyDrive/ColabNotebooks/img_log','acgu.npz')
CHARS = np.load(ACGU_PATH,allow_pickle=True)['data']
DB_PATH = os.path.join('/content/drive/MyDrive/ColabNotebooks/img_log','dot_bracket.npz')
DOT_BRACKET = np.uint8(np.load(DB_PATH,allow_pickle=True)['data'])

def normalize_pwm(pwm, factor=None, MAX=None):
    if MAX is None:
        MAX = np.max(np.abs(pwm))
    pwm = pwm/MAX
    if factor:
        pwm = np.exp(pwm*factor)
    norm = np.outer(np.ones(pwm.shape[0]), np.sum(np.abs(pwm), axis=0))
    return pwm/norm

def get_nt_height(pwm, height, norm):

    def entropy(p):
        s = 0
        for i in range(len(p)):
            if p[i] > 0:
                s -= p[i]*np.log2(p[i])
        return s

    num_nt, num_seq = pwm.shape
    heights = np.zeros((num_nt,num_seq))
    for i in range(num_seq):
        if norm == 1:
            total_height = height
        else:
            total_height = (np.log2(num_nt) - entropy(pwm[:, i]))*height
        
        heights[:,i] = np.floor(pwm[:,i]*np.minimum(total_height, height*2))

    return heights.astype(int)

def get_nt_height(pwm, height, norm):

    def entropy(p):
        s = 0
        for i in range(len(p)):
            if p[i] > 0:
                s -= p[i]*np.log2(p[i])
        return s

    num_nt, num_seq = pwm.shape
    heights = np.zeros((num_nt,num_seq))
    for i in range(num_seq):
        if norm == 1:
            total_height = height
        else:
            total_height = (np.log2(num_nt) - entropy(pwm[:, i]))*height
        
        heights[:,i] = np.floor(pwm[:,i]*np.minimum(total_height, height*2))

    return heights.astype(int)

def seq_logo(pwm, height=30, nt_width=10, norm=0, alphabet='rna', colormap='standard'):

    heights = get_nt_height(pwm, height, norm)
    num_nt, num_seq = pwm.shape
    width = np.ceil(nt_width*num_seq).astype(int)
    
    max_height = height*2
    logo = np.ones((max_height, width, 3)).astype(int)*255
    for i in range(num_seq):
        nt_height = np.sort(heights[:,i])
        index = np.argsort(heights[:,i])
        remaining_height = np.sum(heights[:,i])
        offset = max_height-remaining_height

        for j in range(num_nt):
            if nt_height[j] <=0 :
                continue
            # resized dimensions of image
            nt_img = np.array(Image.fromarray(CHARS[index[j]]).resize((nt_width,nt_height[j])))
            # determine location of image
            height_range = range(remaining_height-nt_height[j], remaining_height)
            width_range = range(i*nt_width, i*nt_width+nt_width)
            # 'annoying' way to broadcast resized nucleotide image
            if height_range:
                for k in range(3):
                    for m in range(len(width_range)):
                        logo[height_range+offset, width_range[m],k] = nt_img[:,m,k]

            remaining_height -= nt_height[j]

    return logo.astype(np.uint8)

def dot_logo(pwm, height=30, nt_width=10, norm=0, alphabet='rna', colormap='standard'):
    heights = get_nt_height(pwm, height, norm)
    num_nt, num_seq = pwm.shape
    width = np.ceil(nt_width*num_seq).astype(int)
    
    max_height = height*2
    logo = np.ones((max_height, width, 3)).astype(int)*255
    for i in range(num_seq):
        nt_height = np.sort(heights[:,i])
        index = np.argsort(heights[:,i])
        remaining_height = np.sum(heights[:,i])
        offset = max_height-remaining_height

        for j in range(num_nt):
            if nt_height[j] <=0 :
                continue
            # resized dimensions of image
            nt_img = np.array(Image.fromarray(DOT_BRACKET[index[j]]).resize((nt_width,nt_height[j])))
            # determine location of image
            height_range = range(remaining_height-nt_height[j], remaining_height)
            width_range = range(i*nt_width, i*nt_width+nt_width)
            # 'annoying' way to broadcast resized nucleotide image
            if height_range:
                for k in range(3):
                    for m in range(len(width_range)):
                        logo[height_range+offset, width_range[m],k] = nt_img[:,m,k]

            remaining_height -= nt_height[j]

    return logo.astype(np.uint8)

def plot_saliency(X, W, nt_width=100, norm_factor=3, str_null=None, outdir="results/"):
    # filter out zero-padding
    # W = savgol_filter(W, 3, 1, axis=1,mode='nearest')
    plot_index = np.where(np.sum(X[:4,:], axis=0)!=0)[0]
    num_nt = len(plot_index)
    trace_width = num_nt*nt_width
    trace_height = 400
    
    seq_str_mode = False
    if X.shape[0]>4:
        seq_str_mode = True
        assert str_null is not None, "Null region is not provided."

    # sequence logo
    img_seq_raw = seq_logo(X[:4, plot_index], height=nt_width, nt_width=nt_width*5//4)

    if seq_str_mode:
        # structure line
        str_raw = X[4, plot_index]
        if str_null.sum() > 0:
            str_raw[str_null.T==1] = -0.01

        line_str_raw = np.zeros(trace_width)
        for v in range(str_raw.shape[0]):
            line_str_raw[v*nt_width:(v+1)*nt_width] = (1-str_raw[v])*trace_height 
            # i+=1
        img_str_raw = dot_logo(X[4:, plot_index], height=nt_width, nt_width=nt_width*5//4)

    # sequence saliency logo
    seq_sal = normalize_pwm(W[:4, plot_index], factor=norm_factor)
    img_seq_sal_logo = seq_logo(seq_sal, height=nt_width*5, nt_width=nt_width*5//4)
    img_seq_sal = np.array(Image.fromarray(W[:4, plot_index].sum(axis=0).reshape(1,len(plot_index))).resize((trace_width*5, trace_height)))

    if seq_str_mode:
        # structure saliency logo
        str_sal = W[4, plot_index].reshape(1,-1)
        img_str_sal = np.array(Image.fromarray(str_sal).resize((trace_width*5, trace_height)))

    # plot    
    #fig = plt.figure(figsize=(10.1,2))
    plt.style.use('default')
    fig = plt.figure(figsize=(11,3))
    gs = gridspec.GridSpec(nrows=5, ncols=1, height_ratios=[2.5, 0.25, 0.5, 0.5, 0.25])
    cmap_reversed = mpl.cm.get_cmap('Spectral_r')             # jet, Spectral_r, coolwarm, RdBu_r

    ax = fig.add_subplot(gs[0, 0])
    ax.axis('off')
    ax.imshow(img_seq_sal_logo)

    ax = fig.add_subplot(gs[1, 0])
    ax.axis('off')
    ax.imshow(img_seq_sal, cmap=cmap_reversed)

    ax = fig.add_subplot(gs[2, 0]) 
    ax.axis('off')
    ax.imshow(img_seq_raw)

    if seq_str_mode:
        ax = fig.add_subplot(gs[4, 0]) 
        ax.axis('off')
        ax.imshow(img_str_sal, cmap=cmap_reversed)

        ax = fig.add_subplot(gs[3, 0]) 
        ax.axis('off')
        ax.imshow(img_str_raw)
    
    plt.subplots_adjust(wspace=0, hspace=0)
    
    # save figure
    filepath = outdir
    fig.savefig(filepath, format='pdf', dpi=300, bbox_inches='tight')
    plt.close('all')
    return fig


def RNA_plot(inputPath, resultsF, index, smooth_steps=3):
    '''
    '''
    testData = pd.read_csv(inputPath,sep='\t',header=None,index_col=0,names=['drug', 'rna', 'SMILES', 'Sequence', 'Structure', 'prob'])
    df_p = np.zeros((5,6,31))
    df_p_median = np.zeros((6,31))
    resM = pd.read_table(resultsF + '/merge_results.txt',sep='\t',header=None,names=['ids','drug', 'rna', 'SMILES', 'Sequence', 'Structure', 'prob'])
    shreshold = resM.loc[index,'prob']
    for i in range(5):
        if pd.read_table(resultsF + '/CV_' + str(i+1) + '/results_sort.txt',sep='\t').loc[0,'prob']<shreshold:
            continue
        try:
            df_tmp_p = pd.read_table(resultsF + '/CV_' + str(i+1) + '/0_salency_P_'+str(index)+'.txt',sep=',',header=None)
            df_tmp_pe = pd.read_table(resultsF + '/CV_' + str(i+1) + '/0_salency_Pe_'+str(index)+'.txt',sep=',',header=None)
            df_tmp = pd.concat([df_tmp_p, df_tmp_pe], axis=0)
            df_tmp = df_tmp.values
            if pd.read_table(resultsF + '/CV_' + str(i+1) + '/results_sort.txt',sep='\t').loc[0,'prob']==shreshold:
                df_p_median = df_tmp.copy()
            df_tmp = (df_tmp-df_tmp.min(axis=1)[:,np.newaxis])/(df_tmp.max(axis=1)[:,np.newaxis]-df_tmp.min(axis=1)[:,np.newaxis])
        except:
            df_tmp = np.zeros((6,31))
        df_p[i,:,:] = df_tmp.reshape(1,6,31)

    df_p = df_p.sum(axis=0)/3
    df_p = pd.DataFrame(df_p)
    df_p_median = pd.DataFrame(df_p_median)


    df3 = pd.Series(list(testData['Sequence'][index]+'AUGC'))
    df4=(pd.get_dummies(df3)).T
    df4 = df4.iloc[:,:31]
    df2=pd.DataFrame(index=np.arange(2), columns=np.arange(31)).fillna(1)
    merge = pd.concat([df4,df2],ignore_index=True)
    df_final=df_p*merge
    df_final_median = df_p_median*merge
    
    window_size = 8
    max_value = 0
    for i in range(0,df_final.shape[1]-window_size+1,1):
        if df_final.iloc[:4,i:i+window_size].values.mean() >= max_value:
            max_index = i
            max_value = df_final.iloc[:4,i:i+window_size].values.mean()

    max_value = 0
    for j in range(0,df_final.shape[1]-window_size+1,1):
        if df_final.iloc[4:5,j:j+window_size].values.mean() >= max_value:
            max_jndex = j
            max_value = df_final.iloc[4:5,j:j+window_size].values.mean()
    
    if max_jndex <= max_index and max_jndex+window_size >= max_index:
        df_final.iloc[:,:max_jndex] = 0
        df_final.iloc[:,max_index+window_size:] = 0
    elif max_index <= max_jndex and max_index+window_size >= max_jndex:
        df_final.iloc[:,:max_index] = 0
        df_final.iloc[:,max_jndex+window_size:] = 0
    else:
        df_final.iloc[:,:min(max_index,max_jndex)] = 0
        df_final.iloc[:,min(max_index,max_jndex)+window_size:max(max_index,max_jndex)] = 0
        df_final.iloc[:,max(max_index,max_jndex)+window_size:] = 0

    if smooth_steps >= 3:
        df_final.iloc[:4,:] = df_final.iloc[:4,:].sum(axis=0)
        df_final_median.iloc[:4,:] = df_final_median.iloc[:4,:].sum(axis=0)
        
        df_final = savgol_filter(df_final, smooth_steps, 1, axis=1, mode='nearest')
        df_final_median = savgol_filter(df_final_median, smooth_steps, 1, axis=1, mode='nearest')
        
        df_final=df_final*merge
        df_final_median=df_final_median*merge
    else:
        pass
    

    df3 = pd.Series(list(testData['Structure'][index]+'.()'))
    df5=(pd.get_dummies(df3)).T
    df5 = df5.iloc[:,:31]
    merge = pd.concat([df4,df5],ignore_index=True)

    w = plot_saliency(merge.iloc[:7,:].values, df_final.iloc[:5,:].values, nt_width=100, norm_factor=3, str_null=np.zeros(31), outdir=resultsF + '/2_RNA_final_'+str(index)+'.pdf')
    w_median = plot_saliency(merge.iloc[:7,:].values, df_final_median.iloc[:5,:].values, nt_width=100, norm_factor=3, str_null=np.zeros(31), outdir=resultsF + '/3_RNA_final_'+str(index)+'.pdf')

    return w, w_median

def load(inputPath, select_cv=0):
    restsAll = pd.DataFrame({})
    for i in range(5):
        resTmp = pd.read_csv(inputPath+'/CV_'+str(i+1)+'/results_sort.txt', sep='\t', index_col=None,)
        if i==0:
            restsAll = pd.concat([restsAll,resTmp['index']],axis=1)
            restsAll = pd.concat([restsAll,resTmp['drug']],axis=1)
            restsAll = pd.concat([restsAll,resTmp['rna']],axis=1)
        restsAll = pd.concat([restsAll,resTmp['prob']],axis=1)
    restsAll.columns = ['index','drug','rna','probs1','probs2','probs3','probs4','probs5']
    restsAll['median'] = restsAll[['probs1','probs2','probs3','probs4','probs5']].median(axis=1)
    drug_visualization,rna_visualization = [],{'merge':[],'median':[]}
    for i in range(len(restsAll.index)):
        fig_merge, fig_median = RNA_plot(inputPath+'/merge_results.txt',inputPath,i,3)
        rna_visualization['merge'].append(fig_merge)
        rna_visualization['median'].append(fig_median)
    rna_visualization = pd.DataFrame(rna_visualization)
    print("There are "+str(len(rna_visualization))+" of interactions has been loaded...")
    print("Please use visualization.loc[index,'merge'],index=(1,2,3..."+str(len(rna_visualization))+") to visualize the merge 5-CV binding sites prediction")
    print("Please use visualization.loc[index,'median'],index=(1,2,3..."+str(len(rna_visualization))+") to visualize the final results' binding sites prediction")
    return restsAll, rna_visualization
