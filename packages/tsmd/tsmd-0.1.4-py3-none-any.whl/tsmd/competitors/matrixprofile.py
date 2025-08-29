import numpy as np
from joblib import Parallel,delayed
import tsmd.tools.distance as distance


import warnings
warnings.filterwarnings('ignore')

class MatrixProfile(object): 
    """STOMP algorithm for motif discovery.

        Parameters
        ----------
        n_patterns : int 
            Number of patterns to detect.
        wlen : int
            Window length.
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
    def __init__(self,n_patterns:int,wlen:int,distance_name:str,distance_params = dict(),radius_ratio = 3,n_jobs = 1) -> None:
    
        self.n_patterns = n_patterns
        self.radius_ratio = radius_ratio
        self.wlen = wlen
        self.distance_name = distance_name
        self.distance_params = distance_params
        self.n_jobs = n_jobs

    def _search_neighbors(self,idx:int,line:np.ndarray)-> tuple: 
        """Find the indices and distances of non-overlapping neighbors under the radius threshold.

        Parameters
        ----------
        idx : int
            Index of the current line in the cross-distance matrix.
        line : np.ndarray
            A single line of the cross-distance matrix of shape (n_samples,).

        Returns
        -------
        neighbors: np.ndarray
            Indices of neighboring subsequences satisfying the radius condition.
        dists: np.ndarray
            Corresponding distances to those neighbors.
        """


        #initilization
        neighbors = []
        dists = []
        idxs = np.arange(line.shape[0])
        remove_idx = np.arange(max(0,idx-self.wlen+1),min(self.mdim_,idx+self.wlen))
        line[remove_idx] = np.inf

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
                remove_idx = np.arange(max(0,t_idx-self.wlen+1),min(len(line),t_idx+self.wlen))
                line[remove_idx] = np.inf
            
        return neighbors,dists

    def _elementary_profile(self,start:int,end:int)->tuple:
        """Compute elementary profile of a chunk of successive lines of the crossdistance matrix

        Parameters
        ----------
        start : int
            Starting index of the chunk.
        end : int
            Ending index of the chunk (exclusive).

        Returns
        -------
        neighbors: list of np.ndarray 
            Indices of neighbors for each line in the chunk.
        dists: list of np.ndarray 
            Corresponding distances for each neighbor set.
        """
        #initialization
        neighbors =[]
        dists = []
        line = self.distance_.first_line(start)
        mask = np.arange(max(0,start-self.wlen+1), min(self.mdim_,start+self.wlen))
        line[mask] = np.inf
        t_idx = np.argmin(line)
        t_dist = line[t_idx]
        neighbors.append(t_idx)
        dists.append(t_dist)
        
        #main loop
        for i in range(start+1,end): 
            line = self.distance_.next_line()
            mask = np.arange(max(0,i-self.wlen+1), min(self.mdim_,i+self.wlen))
            line[mask] = np.inf
            t_idx = np.argmin(line)
            t_dist = line[t_idx]
            neighbors.append(t_idx)
            dists.append(t_dist)
        return neighbors,dists

    def profile_(self)->None: 
        """Compute the profile for all subsequences using parallel computation.
        This method divides the task into chunks based on `n_jobs`, and collects
        the neighborhood indices and distances for each subsequence.

        Returns
        -------
        self : MatrixProfile
            The updated MatrixProfile instance with `idxs_` and `dists_` attributes set.
    """
        #divide the signal accordingly to the number of jobs
        set_idxs = np.linspace(0,self.mdim_,self.n_jobs+1,dtype=int)
        set_idxs = np.vstack((set_idxs[:-1],set_idxs[1:])).T

        # set the parrallel computation
        results = Parallel(n_jobs=self.n_jobs, prefer="processes")(
            delayed(self._elementary_profile)(*set_idx)for set_idx in set_idxs
        )

        idxs,dists = list(zip(*results))

        self.idxs_ = np.hstack(idxs)
        self.dists_ = np.hstack(dists)
        return self

    def find_patterns_(self): 
        """Identify the most representative motifs by first running a PairMotifs search, 
        then scanning all subsequences to determine which ones fall within a radius `r` of the discovered motif pairs."""
        profile = self.dists_.copy()
        mask = []
        patterns = []

        for _ in np.arange(self.n_patterns): 
            min_idx = np.argmin(profile)
            if profile[min_idx]==np.inf: 
                break
            line = self.distance_.first_line(min_idx)
            line[mask] = np.inf
            p_idxs,dists = self._search_neighbors(min_idx,line)
            p_idxs = np.hstack((np.array([min_idx]),p_idxs))
            patterns.append(p_idxs)
            mask += np.hstack([np.arange(max(0,idx-self.wlen+1),min(self.mdim_,idx+self.wlen)) for idx in p_idxs]).astype(int).tolist()
            profile[mask] = np.inf
        
        self.patterns_ = patterns

    def fit(self,signal:np.ndarray)->None:
        """Fit STOMP
        
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
        self.mdim_ = len(signal)-self.wlen+1 
        self.distance_ = getattr(distance,self.distance_name)(self.wlen,**self.distance_params)
        self.distance_.fit(signal)

        #Compute neighborhood
        self.profile_()
        #find patterns
        self.find_patterns_()

        return self

    @property
    def prediction_mask_(self):
        mask = np.zeros((self.n_patterns,self.signal_.shape[0]))
        for i,p_idxs in enumerate(self.patterns_):
            for idx in p_idxs.astype(int):
                mask[i,idx:idx+self.wlen]=1 
        #remove null lines
        mask=mask[~np.all(mask == 0, axis=1)]
        return mask