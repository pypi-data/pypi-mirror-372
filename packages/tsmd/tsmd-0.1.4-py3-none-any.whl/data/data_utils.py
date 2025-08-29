import numpy as np
import sys 
import os
import json
from kshape.core import KShapeClusteringCPU 
from sklearn.metrics import adjusted_rand_score

import tsmd.tools.distance as distance


def get_metadata(labels,signal):

    metadata={}

    present_labels=np.unique(labels)
    present_labels=present_labels[present_labels!='-1']
    metadata['motifs_id']=dict(zip(present_labels,present_labels))
    
    metadata['motif_count']={}
    metadata['motif_avg_length']={}
    metadata['motif_max_length']={}
    metadata['motif_min_length']={}
    metadata['motif_median_length']={}
    metadata['motif_std_length']={}
    metadata['motif_empirical_radius']={}

    extended_labels1=np.concatenate((['-1'],labels))[:-1]
    extended_labels2=np.concatenate((labels,['-1']))[1:]
    for lab in present_labels:

        motifs_start= np.where((labels==lab) & (extended_labels1!=lab))[0]
        motifs_end = np.where((labels==lab)& (extended_labels2!=lab))[0]
        motifs_length=motifs_end-motifs_start+1
        empirical_radius=compute_empirical_radius(signal,motifs_start,motifs_end)

        metadata['motif_count'][lab]=int(motifs_length.shape[0])
        metadata['motif_avg_length'][lab]=float(np.mean(motifs_length))
        metadata['motif_max_length'][lab]=int(np.max(motifs_length))
        metadata['motif_min_length'][lab] = int(np.min(motifs_length))
        metadata['motif_median_length'][lab]= int(np.median(motifs_length))
        metadata['motif_std_length'][lab]= float(np.std(motifs_length))
        metadata['motif_empirical_radius'][lab] = float(np.round(empirical_radius,2))

    

    min_empirical_radius_id=min(metadata['motif_empirical_radius'],key=metadata['motif_empirical_radius'].get)
    max_empirical_radius_id=max(metadata['motif_empirical_radius'],key=metadata['motif_empirical_radius'].get)

    metadata['min_empirical_radius']={min_empirical_radius_id: metadata['motif_empirical_radius'][min_empirical_radius_id]}
    metadata['max_empirical_radius']={max_empirical_radius_id: metadata['motif_empirical_radius'][max_empirical_radius_id]}

    return metadata

def compute_empirical_radius(signal,motifs_start,motifs_end):

    motif_min_length= np.min(motifs_end-motifs_start+1)

    max_dist=0
    dist=distance.UnitEuclidean(motif_min_length)
    dist.fit(signal)

    for i in range(motifs_start.shape[0]-1):
        for j in range(i+1,motifs_start.shape[0]):
            min_dist=np.inf
            for k in range(motifs_start[i],motifs_end[i]-motif_min_length+2):
                for l in range(motifs_start[j],motifs_end[j]-motif_min_length+2):
                    curr_dist=dist.individual_distance(k,l)
                    min_dist=min(curr_dist,min_dist)
            max_dist=max(min_dist,max_dist)

    return max_dist/2

def dataset_metadata(PATH):
    dataset_md = {}

    dataset_md['nb_motifs']=0
    dataset_md['motifs_id'] = {}
    dataset_md['motif_count']={}
    dataset_md['nb_present_TS']={}

    min_nb_motifs=np.inf
    max_nb_motifs=0
    mean_nb_motifs=0
    kshape_mean_score=0

    for file in os.listdir(PATH):

        f = open(PATH + file)
        metadata=json.load(f)

        nb_motifs=len(metadata['motifs_id'])
        mean_nb_motifs+=nb_motifs
        if nb_motifs>max_nb_motifs:
            max_nb_motifs=nb_motifs
        if nb_motifs<min_nb_motifs:
            min_nb_motifs=nb_motifs
        
        kshape_mean_score+=metadata['kshape_score']

        for key in metadata['motifs_id']:
            if key not in dataset_md['motifs_id']:
                dataset_md['motifs_id'][key]=key
                dataset_md['motif_count'][key]=metadata['motif_count'][key]
                dataset_md['nb_present_TS'][key]=1
            else:
                dataset_md['motif_count'][key]+=metadata['motif_count'][key]
                dataset_md['nb_present_TS'][key]+=1
    
    mean_nb_occurences=np.array(list(dataset_md['motif_count'].values()))/np.array(list(dataset_md['nb_present_TS'].values()))
    dataset_md['mean_nb_occurences']=dict(zip(dataset_md['motifs_id'].values(),mean_nb_occurences))
    
    mean_nb_motifs/=len(os.listdir(PATH))

    kshape_mean_score/=len(os.listdir(PATH))

    dataset_md["mean_nb_motifs"]=mean_nb_motifs
    dataset_md["min_nb_motifs"]=min_nb_motifs
    dataset_md["max_nb_motifs"]=max_nb_motifs

    dataset_md['nb_motifs']=len(dataset_md['motifs_id'])
    
    dataset_md['kshape_mean_score']=kshape_mean_score

    return dataset_md
        
def get_params_by_ts(metadata_path):
    #given a json corresponding to a Time Series, returns the ideal parameters used to run the algos 
    f = open(metadata_path)
    metadata=json.load(f)
    K=len(metadata['motifs_id'])
    R_min=min(metadata['motif_empirical_radius'].values())
    R_max=max(metadata['motif_empirical_radius'].values())
    R_mean=np.round(np.average(np.array(list(metadata['motif_empirical_radius'].values())),weights=np.array(list(metadata['motif_count'].values()))),2)

    w_mean=np.average(np.array(list(metadata['motif_avg_length'].values())),weights=np.array(list(metadata['motif_count'].values())))

    intermediate_median=[]
    for length,count in zip(metadata['motif_avg_length'].values(),metadata['motif_count'].values()):
        intermediate_median+=count*[length]
    w_median=np.median(intermediate_median)

    w_min=min(metadata['motif_min_length'].values())
    w_max=max(metadata['motif_max_length'].values())
    k=np.array(list(metadata['motif_count'].values()))
    k_max= max(k)

    return K,R_min,R_max,R_mean,w_mean,w_median,w_min,w_max,k,k_max

def transform_label(L:np.ndarray)->list: 
    """Transfom binary mask to a list of start and ends

    Args:
        L (np.ndarray): binary mask, shape (n_label,length_time_series)

    Returns:
        list: start and end list. 
    """
    lst = []
    for line in L: 
        if np.count_nonzero(line)!=0:
            line = np.hstack(([0],line,[0]))
            diff = np.diff(line)
            start = np.where(diff==1)[0]+1
            end = np.where(diff==-1)[0]
            lst.append(np.array(list(zip(start,end))))
    return np.array(lst,dtype=object)


def compute_K_shape(labels,signal):
    
    occurences=[]
    occurences_labels=[]

    present_labels=np.unique(labels)
    present_labels=present_labels[present_labels!='-1']
    extended_labels1=np.concatenate((['-1'],labels))[:-1]
    extended_labels2=np.concatenate((labels,['-1']))[1:]
    max_length=0

    for lab in present_labels:
        motifs_start= np.where((labels==lab) & (extended_labels1!=lab))[0]
        motifs_end = np.where((labels==lab)& (extended_labels2!=lab))[0]
        for i in range(motifs_start.shape[0]):
            s,e=motifs_start[i],motifs_end[i]
            if e-s>max_length:
                max_length=e-s
            occurences.append(signal[s:e])
            occurences_labels.append(lab)
    #padding the occurences with 0 so they all have the same length
    occurences=np.expand_dims(np.array([np.pad(occ,(0,max_length-occ.shape[0])) for occ in occurences]),axis=2)
    num_clusters=present_labels.shape[0]    
    ksc = KShapeClusteringCPU(num_clusters, centroid_init='zero', max_iter=100, n_jobs=-1)
    ksc.fit(occurences)
    kshape_labels = ksc.labels_
     
    clustering_score=adjusted_rand_score(occurences_labels,kshape_labels)

    return clustering_score

