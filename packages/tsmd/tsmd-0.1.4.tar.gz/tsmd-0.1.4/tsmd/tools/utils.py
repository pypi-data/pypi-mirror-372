import numpy as np
import json 

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

def transform_label_to_mask(labels):
    n=labels.shape[0]
    unique_labels=np.unique(labels)
    unique_labels=unique_labels[unique_labels!='-1']
    nb_motifs=unique_labels.shape[0]
    mask=np.zeros((nb_motifs,n))
    for i in range(nb_motifs):
        mask[i,labels==unique_labels[i]]=1
    return mask 

def get_params_by_ts(metadata_path):
    #given a json corresponding to a Time Series, returns the ideal parameters used to run the algos 
    f = open(metadata_path)
    metadata=json.load(f)
    K=len(metadata['motifs_id'])
    R_min=min(metadata['motif_empirical_radius'].values())
    R_max=max(metadata['motif_empirical_radius'].values())
    R_mean=np.round(np.average(np.array(list(metadata['motif_empirical_radius'].values())),weights=np.array(list(metadata['motif_count'].values()))),2)

    w_mean=int(np.average(np.array(list(metadata['motif_avg_length'].values())),weights=np.array(list(metadata['motif_count'].values()))))

    intermediate_median=[]
    for length,count in zip(metadata['motif_avg_length'].values(),metadata['motif_count'].values()):
        intermediate_median+=count*[length]
    w_median=int(np.median(intermediate_median))
    w_std=int(max(metadata['motif_std_length'].values()))

    w_min=int(min(metadata['motif_min_length'].values()))
    w_max=int(max(metadata['motif_max_length'].values()))
    k=np.array(list(metadata['motif_count'].values()))
    
    k_max= max(k)

    return K,R_min,R_max,R_mean,w_mean,w_median,w_std,w_min,w_max,k,k_max