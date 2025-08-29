import numpy as np
from joblib import Parallel,delayed
import tsmd.tools.distance as distance
from functools import partial


import warnings
warnings.filterwarnings('ignore')

class PanMatrixProfile(object): 
    """STOMP algorithm for motif discovery.

        Parameters
        ----------
        n_patterns : int 
            Number of patterns to detect.
        min_wlen : int
            Minimium window length.
        max_wlen : int 
            Maximum window length.
        radius_ratio : float, optional (default=3.0)
            Threshold scaling factor for pattern inclusion. (Given a Motif Pair with distance d, the threshold is equal to radius_ratio*d)
        distance_name : str, optional, default="UnitEuclidean"
            Name of the distance.
        distance_params : dict, optional (default=dict())
            Additional distance parameters. 
        n_jobs : int, optional (default=1)
            Number of jobs.
        
        Attributes
        ----------
        prediction_mask_ : np.ndarray of shape (n_patterns, n_samples)
            Binary mask indicating the presence of motifs across the signal.  
            Each row corresponds to one discovered motif, and each column to a time step.  
            A value of 1 means the motif is present at that time step, and 0 means it is not.
        """
    def __init__(self,n_patterns:int,min_wlen:int,max_wlen:int,distance_name:str,distance_params = dict(),radius_ratio = 3,normalized=False,n_jobs = 1) -> None:
    
        self.n_patterns = n_patterns
        self.radius_ratio = radius_ratio
        self.min_wlen = min_wlen
        self.max_wlen = max_wlen
        self.distance_name = distance_name
        self.distance_params = distance_params
        self.normalized = normalized
        self.n_jobs = n_jobs

    def _search_neighbors(self,wlen_idx:int,seed_idx:int,line:np.ndarray)-> tuple: 
        """Find the indices and distances of non-overlapping neighbors under the radius threshold for a given window length index.

        Parameters
        ----------
        wlen_idx : int 
            Index of the window length (in self.wlens_).
        seed_idx : int
            Index of the current line in the cross-distance matrix.
        line : np.ndarray
            A single line of the cross-distance matrix of shape (n_samples,).

        Returns
        -------
        neighbors : np.ndarray
            Indices of neighboring subsequences satisfying the radius condition.
        dists : np.ndarray
            Corresponding distances to those neighbors.
        """

        #initilization
        neighbors = []
        dists = []
        idxs = np.arange(line.shape[0])
        remove_idx = np.arange(max(0,seed_idx-self.wlens_[wlen_idx]+1),min(line.shape[0],seed_idx+self.wlens_[wlen_idx]))
        line[remove_idx]=np.inf
        #idxs = np.delete(idxs,remove_idx)
        #line = np.delete(line,remove_idx)

        #search loop
        radius = np.min(line)*self.radius_ratio
        t_distance = np.min(line)
        while t_distance < radius:
            #local next neighbor
            t_idx = np.argmin(line)
            t_distance = line[t_idx]
            if line[t_idx] < radius:
                neighbors.append(idxs[t_idx])
                dists.append(line[t_idx])
                #remove window
                remove_idx = np.arange(max(0,t_idx-self.wlens_[wlen_idx]+1),min(len(line),t_idx+self.wlens_[wlen_idx]))
                line[remove_idx] = np.inf
                #idxs = np.delete(idxs,remove_idx)
                #line = np.delete(line,remove_idx)
            
        return neighbors,dists
    
    def _elementary_profile(self,idx:int,start:int,end:int)->tuple:
        """Compute elementary profile of a chunk of successive lines of the crossdistance matrix

        Parameters
        ----------
        start : int
            Starting index of the chunk.
        end : int
            Ending index of the chunk (exclusive).

        Returns
        -------
        neighbors : list of np.ndarray 
            Indices of neighbors for each line in the chunk.
        dists : list of np.ndarray 
            Corresponding distances for each neighbor set.
        """
        #initialization
        neighbors =[]
        dists = []
        line = self.distance_[idx].first_line(start)
        mask = np.arange(max(0,start-self.wlens_[idx]+1), min(self.mdims_[idx],start+self.wlens_[idx]))
        line[mask] = np.inf
        t_idx = np.argmin(line)
        t_dist = line[t_idx]
        neighbors.append(t_idx)
        dists.append(t_dist)
        
        #main loop
        for i in range(start+1,end): 
            line = self.distance_[idx].next_line()
            mask = np.arange(max(0,i-self.wlens_[idx]+1), min(self.mdims_[idx],i+self.wlens_[idx]))
            line[mask] = np.inf
            t_idx = np.argmin(line)
            t_dist = line[t_idx]
            neighbors.append(t_idx)
            dists.append(t_dist)
        return neighbors,dists

    def profile_(self,idx:int)->np.ndarray: 
        """Compute the profile for all subsequences using parallel computation for a given window length index.
        This method divides the task into chunks based on `n_jobs`, and collects
        the neighborhood indices and distances for each subsequence.
        Parameters
        ----------
        idx : int
            Index of the window length (in `self.wlens_`).

        Returns
        -------
        dists : np.ndarray
            The Matrix Profile, containing the minimal distances for each subsequence.
        idxs : np.ndarray 
            The Index Profile, containing the indices of the nearest neighbors.
        """

        #divide the signal accordingly to the number of jobs
        set_idxs = np.linspace(0,self.mdims_[idx],self.n_jobs+1,dtype=int)
        set_idxs = np.vstack((set_idxs[:-1],set_idxs[1:])).T

        # set the parrallel computation
        results = Parallel(n_jobs=self.n_jobs, prefer="processes")(
            delayed(partial(self._elementary_profile,idx))(*set_idx)for set_idx in set_idxs
        )

        idxs,dists = list(zip(*results))

        return np.hstack(dists),np.hstack(idxs)

    def _temporary_mask(self,wlen_idx:int,mask:list,patterns:list)->list: 
        """Create mask associated with the current research windows

        Parameters
        ----------
        wlen_idx : int 
            Index of the window length (in self.wlens_).
        mask : list
            Current mask.
        patterns :list 
            List of patterns already detected.

        Returns
        -------
        mask : list 
            Mask for the search of neighbors.
        """
        t_mask = mask.copy()
        for _, p_idxs in patterns: 
            for p_idx in p_idxs: 
                t_mask += np.arange(max(0,p_idx-self.wlens_[wlen_idx]+1),p_idx+1).astype(int).tolist()
        t_mask = np.array(t_mask)
        keep_idx = np.where(t_mask<=self.mdims_[wlen_idx])
        return t_mask[keep_idx].tolist()

    def find_patterns_(self): 
        """Identify the most representative motifs"""
        profiles = self.profiles_.copy()
        mask = []
        patterns = []

        for iteration in np.arange(self.n_patterns): 
            if iteration == 0: 
                min_idx = np.argmin(profiles)
                wlen_idx, seed_idx = np.unravel_index(min_idx,profiles.shape)
                line = self.distance_[wlen_idx].first_line(seed_idx)
            else: 
                overlapping = True
                while overlapping and not np.all(profiles == np.inf): 
                    min_idx = np.argmin(profiles)
                    wlen_idx, seed_idx = np.unravel_index(min_idx,profiles.shape)
                    t_mask = self._temporary_mask(wlen_idx,mask,patterns)
                    if seed_idx not in t_mask: 
                        overlapping = False
                    else: 
                        profiles[:,seed_idx] = np.inf
                if not overlapping:
                    line = self.distance_[wlen_idx].first_line(seed_idx)
                    line[t_mask] = np.inf

            if np.all(profiles == np.inf):
                break
            
            p_idxs,dists = self._search_neighbors(wlen_idx,seed_idx,line)
            p_idxs = np.hstack((np.array([seed_idx]),p_idxs))
            patterns.append((self.wlens_[wlen_idx],p_idxs))
            mask += np.hstack([np.arange(max(0, idx - self.min_wlen +1),min(self.mdims_[wlen_idx],idx+self.wlens_[wlen_idx])) for idx in p_idxs]).astype(int).tolist()
            profiles[:,mask] = np.inf

        self.test_ = profiles
        
        self.patterns_ = patterns

    def fit(self,signal:np.ndarray)->None:
        """Fit PanMP
        
        Parameters
        ----------
        signal : numpy array of shape (n_samples, )
            The input samples (time series length).
        
        Returns
        -------
        self : object
            Fitted estimator.
        """
        
        #initialisation
        self.signal_ = signal
        self.profiles_ = []
        self.idxs_ = []
        self.distance_ = []
        self.wlens_ = np.arange(self.min_wlen,self.max_wlen+1)
        self.mdims_ = signal.shape[0] - self.wlens_ + 1
        for i,wlen in enumerate(self.wlens_):
            self.distance_.append(getattr(distance,self.distance_name)(self.wlens_[i],**self.distance_params))
            self.distance_[i].fit(signal)

            #Compute profile and idxs
            profile,idxs = self.profile_(i)
            gap = self.wlens_[i] - self.min_wlen
            if gap>0: 
                gap_profile = np.full(gap,np.inf)
                gap_idxs = np.full(gap,np.nan)
                profile = np.hstack((profile,gap_profile))
                idxs = np.hstack((idxs,gap_idxs))
            self.profiles_.append(profile)
            self.idxs_.append(idxs)
        
        self.profiles_ = np.array(self.profiles_)
        self.idxs_ = np.array(self.idxs_)

        if self.normalized: 
            self.profiles_ = self.profiles_ / np.sqrt(self.wlens_).reshape(-1,1)

        #find patterns
        self.find_patterns_()

        return self

    @property
    def prediction_mask_(self):
        mask = np.zeros((self.n_patterns,self.signal_.shape[0]))
        for i,(wlen,p_idxs) in enumerate(self.patterns_):
            for idx in p_idxs:
                mask[i,int(idx):int(idx+wlen)] =1 
        #remove null lines
        mask=mask[~np.all(mask == 0, axis=1)]
        return mask
