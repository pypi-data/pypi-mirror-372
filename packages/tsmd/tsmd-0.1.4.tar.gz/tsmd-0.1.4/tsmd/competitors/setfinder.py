import numpy as np
from joblib import Parallel,delayed
import tsmd.tools.distance as distance
import itertools as it 


import warnings
warnings.filterwarnings('ignore')

class Baseline(object): 
    """SetFinder algorithm for motif discovery.

    Parameters
    ----------
    n_patterns : int 
        Number of patterns to detect.
    radius : float
        Threshold factor for pattern inclusion.
    wlen : int
        Window length.
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

    def __init__(self,n_patterns:int, radius:int, wlen:int, distance_name:str = "UnitEuclidean", distance_params = dict(), n_jobs = 1) -> None:

        self.n_patterns = n_patterns
        self.radius = radius
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
        remove_idx = np.arange(max(0,idx-self.wlen+1),min(line.shape[0],idx+self.wlen))
        line[remove_idx] = np.inf
        #idxs = np.delete(idxs,remove_idx)
        #line = np.delete(line,remove_idx)

        #search loop
        t_distance = np.min(line)
        while t_distance < self.radius:
            #local next neighbor
            t_idx = np.argmin(line)
            t_distance = line[t_idx]
            if line[t_idx] < self.radius:
                neighbors.append(idxs[t_idx])
                dists.append(line[t_idx])
                #remove window
                remove_idx = np.arange(max(0,t_idx-self.wlen+1),min(len(line),t_idx+self.wlen))
                line[remove_idx] = np.inf
                #idxs = np.delete(idxs,remove_idx)
                #line = np.delete(line,remove_idx)

            
        return neighbors,dists
    
    def _elementary_neighborhood(self,start:int,end:int)->tuple:
        """Compute neighborhoods for a chunk of lines from the cross-distance matrix.

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
        t_neighbors,t_dists = self._search_neighbors(start,line)
        neighbors.append(t_neighbors)
        dists.append(t_dists)
        
        #main loop
        for i in range(start+1,end): 
            line = self.distance_.next_line()
            t_neighbors,t_dists = self._search_neighbors(i,line)
            neighbors.append(t_neighbors)
            dists.append(t_dists)

        return neighbors,dists

    def neighborhood_(self)->None: 
        
        """Compute neighborhoods for all subsequences using parallel computation.

            This method divides the task into chunks based on `n_jobs`, and collects
            the neighborhood indices and distances for each subsequence.

            Returns
            -------
            self : Baseline
                The updated Baseline instance with `idxs_` and `dists_` attributes set.
    """
        #divide the signal accordingly to the number of jobs
        set_idxs = np.linspace(0,self.mdim_,self.n_jobs+1,dtype=int)
        set_idxs = np.vstack((set_idxs[:-1],set_idxs[1:])).T

        # set the parrallel computation
        results = Parallel(n_jobs=self.n_jobs, prefer="processes")(
            delayed(self._elementary_neighborhood)(*set_idx)for set_idx in set_idxs
        )

        idxs,dists = list(zip(*results))
        self.idxs_ = list(it.chain(*idxs))
        self.dists_ = list(it.chain(*dists))
        return self

    def find_patterns_(self): 
        """Identify the most representative motifs based on neighbor counts and distance variability.
        """
        

        self.counts_ = np.array([len(lst) for lst in self.idxs_])
        stds = []
        for lst in self.dists_: 
            if len(lst)>0: 
                stds.append(np.std(lst))
            else: 
                stds.append(np.inf)
        self.stds_ = np.array(stds)
        self.sort_idx_ = np.lexsort((self.stds_,-self.counts_))
        patterns = [self.sort_idx_[0]]

        for idx in self.sort_idx_[1:]: 
            if len(patterns) <self.n_patterns: 
                dist_to_patten = np.array([self.distance_.individual_distance(idx,p_idx) for p_idx in patterns])
                if np.all(dist_to_patten > 2*self.radius): 
                    patterns.append(idx)
            else: 
                break

        self.patterns_ = patterns

    def fit(self,signal:np.ndarray)->None:
        """Fit SetFinder
        
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
        self.neighborhood_()
        #find patterns
        self.find_patterns_()

        return self

    @property
    def prediction_mask_(self)->np.ndarray:
        mask = np.zeros((self.n_patterns,self.signal_.shape[0]))
        for i,p_idx in enumerate(self.patterns_):
            mask[i,p_idx:p_idx+self.wlen] =1
            for idx in self.idxs_[p_idx]:
                mask[i,idx:idx+self.wlen] =1 
        #remove null lines
        mask=mask[~np.all(mask == 0, axis=1)]
        return mask