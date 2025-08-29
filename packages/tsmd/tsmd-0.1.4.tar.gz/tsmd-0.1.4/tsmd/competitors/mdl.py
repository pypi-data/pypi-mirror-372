import numpy as np
from joblib import Parallel,delayed
from tsmd.tools.neighborhood import KNN 
import copy


class MDL(object): 
    """MDL algorithm for motif discovery.

        Parameters
        ----------
        min_wlen : int
            Minimium window length.
        max_wlen : int 
            Maximum window length.
        step : int, optional (default=1)
            step used to explore the different window lengths.
        n_bins : int 
            Number of bins used to binarize the signal.
        n_neighbor : int, optional (default=10)
            Number of neighbors used when K nearest neighbors is called.
        max_iter : int, optional (default=50)
            Max number of iteration.
        n_jobs : int, optional (default=1)
            Number of jobs
        verbose: bool, optional(default=False)
            Varbose mode.
        Attributes
        ----------
        prediction_mask_ : np.ndarray of shape (n_patterns, n_samples)
            Binary mask indicating the presence of motifs across the signal.  
            Each row corresponds to one discovered motif, and each column to a time step.  
            A value of 1 means the motif is present at that time step, and 0 means it is not.
            """
    def __init__(self,min_wlen,max_wlen,step=1,n_bins=6,n_neighbor=10,max_iter=50,n_jobs=1,verbose=False) -> None:
        self.min_wlen = min_wlen
        self.max_wlen = max_wlen
        self.step = step
        self.n_bins = n_bins
        self.n_neighbor = n_neighbor
        self.max_iter = max_iter
        self.n_jobs = n_jobs
        self.verbose = verbose

    def _binarized_signal(self,ts): 
        min_val,max_val = np.min(ts),np.max(ts)
        return np.round((ts-min_val)/(max_val-min_val)*(2**self.n_bins-1),0)+1

    ### DESCRIPTION LENGTH FUNCTIONS ###

    def _description_length(self,ts):
        vals,counts = np.unique(ts,return_counts=True)
        probs = counts/ts.shape[0]
        return - np.sum(probs*np.log2(probs))*ts.shape[0]
    
    def _cluster_description_length(self,cluster): 
        cen = cluster["cen"]
        cen_dl = self._description_length(cen)
        sequences_dl = []
        for seq,shift in zip(cluster["seq"],cluster["shift"]): 
            sequences_dl.append(self._description_length(seq-cen[shift:shift+seq.shape[0]]))
        return cen_dl - np.max(sequences_dl) + np.sum(sequences_dl) 

    ### COMPUTE SIMILARITY SEARCH ### 
    
    def _compute_profiles(self): 
        self.profiles_ = []
        self.idxs_ = []
        self.distance_ = []
        self.wlens_ = np.arange(self.min_wlen,self.max_wlen+1,self.step)
        self.mdims_ = self.b_signal_.shape[0] - self.wlens_ + 1

        for wlen in self.wlens_: 
            knn = KNN(self.n_neighbor,wlen,"Euclidean",n_jobs=self.n_jobs)
            knn.fit(self.b_signal_)
            dists,idxs = knn.dists_,knn.idxs_
            gap = wlen -self.wlens_[0]
            if gap > 0: 
                dists = np.pad(dists,((0,gap),(0,0)),constant_values=np.inf)
                idxs = np.pad(idxs,((0,gap),(0,0)),mode="constant",constant_values=-1)
            self.profiles_.append(np.nan_to_num(dists,nan=np.inf))
            self.idxs_.append(idxs)

    def _temporary_mask(self,wlen,mask,idxs):
        t_mask = np.full_like(idxs,False,dtype=bool)
        t_mask[mask] = True
        starts = np.where(np.diff(np.concatenate((np.array([0]),t_mask[:,0])))==1)[0]
        for idx in starts:
            t_mask[np.max((idx-wlen+1,0)):idx] = True   
        mask_idxs = np.where(t_mask==True)[0]
        mask_idxs = np.isin(idxs,mask_idxs)
        t_mask[mask_idxs] = True   
        return t_mask
    
    def _temporary_mask_search(self,wlen,mask):
        t_mask = mask.copy()
        starts = np.where(np.diff(np.concatenate((np.array([0]),t_mask)))==1)[0]
        for idx in starts:
            t_mask[np.max((idx-wlen+1,0)):idx] = True   
        return t_mask
    

    ### CLUSTER CREATION ### 

    def _create_cluster(self,profile,idxs,wlen): 
        try:
            profile = profile.copy()
            mask = self.mask_.copy()

            if np.all(mask==False): 
                seed_idx = np.argmin(profile)
                seed_idx,neigh_idx = np.unravel_index(seed_idx,profile.shape)
                pair_idx = idxs[seed_idx,neigh_idx]
            else: 
                t_mask = self._temporary_mask(wlen,mask,idxs)
                profile[t_mask] = np.inf
                seed_idx = np.argmin(profile)
                seed_idx, neigh_idx = np.unravel_index(seed_idx,profile.shape)
                if profile[seed_idx,neigh_idx]<np.inf:
                    pair_idx = idxs[seed_idx,neigh_idx]
                else:
                    raise ValueError("No new cluster")
            idx1,idx2= seed_idx,pair_idx
            s1,s2 = self.b_signal_[idx1:idx1+wlen], self.b_signal_[idx2:idx2+wlen]
            cluster= dict(
                cen = np.round((s1+s2)/2,0),
                seq = [s1,s2],
                idx = [idx1,idx2],
                shift = [0,0], 
            )
            cluster["cdl"] = self._cluster_description_length(cluster)
            return cluster, self._cluster_creation_bitsave(cluster)
        except:
            return None, -np.inf

                    

    def _cluster_creation_bitsave(self,cluster):  
        cluster_dl = cluster["cdl"]
        sequences_dl = []
        for seq in cluster["seq"]: 
            sequences_dl.append(self._description_length(seq))
        return np.sum(sequences_dl) - cluster_dl


    ### ADD SUBSEQUENCE TO CLUSTER: 

    def _search_nearest_neighbor(self,ts): 
        wlen = ts.shape[0]
        #compute euclidean distance profile
        norm = np.convolve(self.b_signal_**2,np.ones(wlen),mode="valid")
        inn = np.convolve(self.b_signal_,ts[::-1],mode="valid")
        dprofile =  norm - 2*inn + np.sum(ts**2)
        dprofile = np.pad(dprofile,(0,wlen-self.wlens_[0]),constant_values=np.inf)
        t_mask = self._temporary_mask_search(wlen,self.mask_)
        dprofile[t_mask]=np.inf 
        seed_idx = np.argmin(dprofile)
        if dprofile[seed_idx]<np.inf:
            return self.b_signal_[seed_idx:seed_idx+wlen],seed_idx
        else:
            raise ValueError("Cannot find a non overlapping neighbor")     


    def _add_to_cluster(self,cluster,ts,idx): 
        cluster_new = copy.deepcopy(cluster)
        n_ts = len(cluster["seq"])
        cluster_new["cen"] = np.round((cluster["cen"]*n_ts + ts)/(n_ts+1),0)
        cluster_new["seq"].append(ts)
        cluster_new["idx"].append(idx)
        cluster_new["shift"].append(0)
        cluster_new["cdl"] = self._cluster_description_length(cluster_new)
        return cluster_new

    def _add_sequence_cluster(self,cluster):
        try: 
            ts,idx = self._search_nearest_neighbor(cluster["cen"])
            cluster_new = self._add_to_cluster(cluster,ts,idx)
            add_cluster_dl = cluster["cdl"]-cluster_new["cdl"] + self._description_length(ts)
            return cluster_new, add_cluster_dl
        except: 
            return None, -np.inf
            

    ### MERGE CLUSTER ###

    def _merge_clusters(self,cluster1,cluster2): 
        cen1,cen2 = cluster1["cen"],cluster2["cen"]
        l1,l2 = cen1.shape[0],cen2.shape[0]
        n1,n2 = float(len(cluster1["seq"])),float(len(cluster2["seq"]))
        merge_clusters = []
        merge_clusters_bs = []
        #forward cen1 in cen2: 
        for offset in range(l2): 
            l = max(l2,l1+offset)
            cmap2 = np.pad(cen2,(0,l-l2),mode="constant",constant_values = 0)
            weight2 = np.ones_like(cmap2)
            weight2[offset:min(l2,l1+offset)]=n2/(n1+n2)
            cmap1 = np.pad(cen1,(offset,l-l1-offset),mode="constant",constant_values = 0)
            weight1 = np.ones_like(cmap1)
            weight1[offset:min(l2,l1+offset)]=n1/(n1+n2)
            new_cmap = np.sum([cmap1*weight1,cmap2*weight2],axis=0)
            new_cen = np.round(new_cmap[~np.isnan(new_cmap)],0)[:l]
            merge_cluster = dict(
                cen = new_cen,
                seq = cluster1["seq"] + cluster2["seq"],
                idx = cluster1["idx"] + cluster2["idx"],
                shift = [s+offset for s in cluster1["shift"]] + cluster2["shift"]
            )
            merge_cluster["cdl"] = self._cluster_description_length(merge_cluster)
            merge_clusters.append(merge_cluster)
            merge_clusters_bs.append(cluster1["cdl"]+cluster2["cdl"]-merge_cluster["cdl"])
        #forward cen2 in cen1: 
        for offset in range(1,l1): 
            l = max(l1,l2+offset)
            cmap1 = np.pad(cen1,(0,l-l1),mode="constant",constant_values = 0)
            weight1 = np.ones_like(cmap1)
            weight1[offset:min(l1,l2+offset)]=n1/(n1+n2)
            cmap2 = np.pad(cen2,(offset,l-l2-offset),mode="constant",constant_values = 0)
            weight2 = np.ones_like(cmap2)
            weight2[offset:min(l1,l2+offset)]=n2/(n1+n2)
            new_cmap = np.nansum([cmap1*weight1,cmap2*weight2],axis=0)
            new_cen = np.round(new_cmap[~np.isnan(new_cmap)],0)[:l]
            merge_cluster = dict(
                cen = new_cen,
                seq = cluster1["seq"] + cluster2["seq"],
                idx = cluster1["idx"] + cluster2["idx"],
                shift = cluster1["shift"] + [s+offset for s in cluster2["shift"]]
            )
            merge_cluster["cdl"] = self._cluster_description_length(merge_cluster)
            merge_clusters.append(merge_cluster)
            merge_clusters_bs.append(cluster1["cdl"]+cluster2["cdl"]-merge_cluster["cdl"])

        b_merge_cluster_idx = np.argmax(merge_clusters_bs)
        return merge_clusters[b_merge_cluster_idx], merge_clusters_bs[b_merge_cluster_idx]
   
            
    def fit(self,signal): 
        """Fit MDL
        
        Parameters
        ----------
        signal : numpy array of shape (n_samples, )
            The input samples (time series length).
        
        Returns
        -------
        self : object
            Fitted estimator.
        """
        self.signal_ = signal
        self.b_signal_ = self._binarized_signal(signal)

        # compute profiles 
        self._compute_profiles()
        self.mask_ = np.full_like(self.profiles_[0][:,0],False,dtype=bool)

        def add_with_idx(cluster,idx): 
            return self._add_sequence_cluster(cluster),idx

        def merge_with_idx(cluster1,cluster2,lst): 
            return self._merge_clusters(cluster1,cluster2),lst

        #main loop
        iterate = True
        self.clusters_ = []
        iteration = 0
        while iterate & (iteration<self.max_iter): 
            iteration +=1
            clusters_copy = copy.deepcopy(self.clusters_)

            # create new clusters:
            new_clusters = []
            new_clusters_bs = []
            results = Parallel(self.n_jobs)(delayed(self._create_cluster)(profile,idxs,self.wlens_[idx]) for idx,(profile,idxs) in enumerate(zip(self.profiles_,self.idxs_)))
            for new_cluster, new_cluster_bs in results:
                new_clusters.append(new_cluster)
                new_clusters_bs.append(new_cluster_bs)
            #for i,(profile,idxs) in enumerate(zip(self.profiles_,self.idxs_)):
            #    try:
            #        wlen = self.wlens_[i]
            #        new_cluster, new_cluster_bs = self._create_cluster(profile,idxs,wlen)
            #        new_clusters.append(new_cluster)
            #        new_clusters_bs.append(new_cluster_bs)
            #    except: 
            #        new_clusters_bs.append(-np.inf)

            b_new_cluster_idx = np.argmax(new_clusters_bs)
            b_new_cluster_bs = new_clusters_bs[b_new_cluster_idx]

            # add sequence: 
            add_clusters = []
            add_clusters_bs = []
            add_clusters_idx = []
            if len(self.clusters_)>0:
                results = Parallel(self.n_jobs)(delayed(add_with_idx)(cluster,idx) for idx,cluster in enumerate(clusters_copy))
                for (add_cluster,add_cluster_bs),idx in results:    
                    add_clusters.append(add_cluster)
                    add_clusters_bs.append(add_cluster_bs)
                    add_clusters_idx.append(idx)
            else: 
                add_clusters_bs.append(-np.inf)
            b_add_cluster_idx = np.argmax(add_clusters_bs)
            b_add_cluster_bs = add_clusters_bs[b_add_cluster_idx]         

            # merge cluster: 
            merge_clusters = []
            merge_clusters_bs = []
            merge_clusters_idx = []
            if len(self.clusters_)>1: 
                results = Parallel(self.n_jobs)(delayed(merge_with_idx)(clusters_copy[i],clusters_copy[j],[j,i]) for i,j in np.vstack((np.triu_indices(len(self.clusters_),1))).T)
                for (merge_cluster, merge_cluster_bs),lst in results:
                    merge_clusters.append(merge_cluster)
                    merge_clusters_bs.append(merge_cluster_bs)
                    merge_clusters_idx.append(lst)
            else: 
                merge_clusters_bs.append(-np.inf)
            b_merge_cluster_idx = np.argmax(merge_clusters_bs)
            b_merge_cluster_bs = merge_clusters_bs[b_merge_cluster_idx]
            

            # Identify best operation
            b_opts_bs = [b_new_cluster_bs,b_add_cluster_bs,b_merge_cluster_bs]
            if self.verbose: 
                print(f"Iteration {iteration}/{self.max_iter} -- {b_opts_bs}")
            b_idx = np.argmax(b_opts_bs)
            if b_opts_bs[b_idx]>= 0: 
                if b_idx == 0: 
                    new_cluster = new_clusters[b_new_cluster_idx]
                    for idx,seq in zip(new_cluster["idx"],new_cluster["seq"]):
                        self.mask_[idx:idx+seq.shape[0]]=True
                    self.clusters_.append(new_cluster)
                elif b_idx ==1: 
                    add_cluster = add_clusters[b_add_cluster_idx]
                    idx = add_clusters_idx[b_add_cluster_idx]
                    self.clusters_.pop(idx)
                    self.clusters_.append(add_cluster)
                    idx = add_cluster["idx"][-1]
                    wlen = add_cluster["seq"][-1].shape[0]
                    self.mask_[idx:idx+wlen] = True
                else: 
                    merge_cluster = merge_clusters[b_merge_cluster_idx]
                    idxs = merge_clusters_idx[b_merge_cluster_idx]
                    for idx in idxs: 
                        self.clusters_.pop(idx)
                    self.clusters_.append(merge_cluster)
            else: 
                iterate = False
        return self

    @property
    def prediction_mask_(self)->np.ndarray: 
        mask = np.zeros((len(self.clusters_),self.b_signal_.shape[0]))
        for i,cluster in enumerate(self.clusters_): 
            for seq,idx in zip(cluster["seq"],cluster["idx"]): 
                mask[i,idx:idx+seq.shape[0]]=1
        #remove null lines
        mask=mask[~np.all(mask == 0, axis=1)]
        return mask