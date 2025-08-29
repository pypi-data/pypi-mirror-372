import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon

from tsmd.tools.neighborhood import KNN
from tsmd.competitors.competitors_tools.persistence_tools import BasicPersistence,ThresholdPersistenceMST
from tsmd.tools.threshold import otsu_jump
from tsmd.tools.post_processing import PostProcessing

#########################################################################################################################################
#########################################################################################################################################

class BasePersistentPattern(object): 
    """PEPA algorithm for motif discovery.

    Parameters
    ----------
    wlen_for_persistence : int
        Window length. A good heuristic to set the window length for PEPA is to take the average window length minus the standard deviation window length.
    n_patterns : int, optional (default is None)
        Number of patterns to detect. If is None, the number of patterns is inferred.
    n_neighbors : int, optional (default=5)
        Number of neighbors used to construct the graph during the first phase of PEPA.
    jump : int, optional (default=1)
        Number of jumps used to compute persistance cut and birth cut.
    distance_name : str, optional, default="LTNormalizedEuclidean"
        Name of the distance.
    alpha : float, optional (default=10.0)
        Parameter for the distance adjustement.
    beta : float, optional (default=0)
        Parameter for the distance adjustement.
    n_jobs : int, optional (default=1)
        Number of jobs.
    
    Attributes
    ----------
    prediction_mask_ : np.ndarray of shape (n_patterns, n_samples)
        Binary mask indicating the presence of motifs across the signal.  
        Each row corresponds to one discovered motif, and each column to a time step.  
        A value of 1 means the motif is present at that time step, and 0 means it is not.
    """
    def __init__(self,wlen_for_persistence:int, n_patterns = None,n_neighbors=5,jump=1,distance_name_for_persistence = "LTNormalizedEuclidean",alpha =10,beta = 0,individual_birth_cut = False,similar_length = False, similarity = 0.25,n_jobs =1): 
        self.wlen = wlen_for_persistence
        self.n_neighbors = n_neighbors
        self.n_patterns = n_patterns
        self.jump = jump
        self.distance_name = distance_name_for_persistence
       
        self.min_wlen = wlen_for_persistence
        self.alpha = alpha
        self.beta = beta
        self.individual_bith_cut = individual_birth_cut
        self.similar_length = similar_length
        self.similarity = similarity
        self.n_jobs = n_jobs

        self.p_cut_ = None
        self.b_cut_ = None

        self.post_processing_ = PostProcessing(wlen_for_persistence,self.min_wlen,similar_length,similarity)

    def _ktanh(self,X:np.ndarray,alpha=None,beta = None)->np.ndarray:
        if alpha is None: 
            alpha = self.alpha
        if beta is None: 
            beta = self.beta
        norm_factor = np.tanh(beta**2*alpha) - np.tanh(-alpha*(4-beta**2))
        dists =  np.tanh(beta**2*alpha) - np.tanh(-alpha*(X**2-beta**2))
        return 2 * np.sqrt(dists/norm_factor)
    
    
    def _base_persistence(self,signal:np.ndarray)->None: 
        self.knn_ = KNN(self.n_neighbors,self.wlen,self.distance_name,n_jobs=self.n_jobs)
        self.knn_.fit(signal)
        self.base_persistence_ = BasicPersistence()
        self.base_persistence_.fit(self.knn_.filtration_)

    def _thresholds(self)->None: 
        pers = self.get_persistence(True)
        self.p_cut_,self.b_cut_ = otsu_jump(pers[:-1,:-1],jump=self.jump)
        if self.n_patterns is not None:
            idxs = np.where(pers[:,0]<self.b_cut_)[0]
            arr = pers[idxs]
            arr = np.sort(arr[:,1]- arr[:,0])[::-1]
            self.p_cut_ = (arr[self.n_patterns-1]+arr[self.n_patterns])/2

    def _birth_cut_dct(self)->None: 
        """Compute the dictionnary of birth cut per motif
        """
        if self.individual_bith_cut:
            pers = self.get_persistence(True)
            mask = pers[:,1] - pers[:,0] > self.p_cut_
            b_cut_dct = {}
            for line in pers[mask]: 
                if line[0]<= self.b_cut_:
                    b_cut_dct[int(line[-1])] = min(line[1],self.b_cut_)
            self.b_cut_dct_ = b_cut_dct
        else:
            self.b_cut_dct_ = None

    
    def _persistence_with_thresholds(self)->None:
        """Compute persistence based on given thresholds.
        """ 
        self.tpmst_= ThresholdPersistenceMST(persistence_threshold=self.p_cut_,birth_threshold=self.b_cut_,birth_individual_threshold=self.b_cut_dct_) 
        mst = self.base_persistence_.mst_.copy()
        mst[:,-1] = self._ktanh(mst[:,-1],self.alpha,self.beta)
        self.tpmst_.fit(mst)

    def _fit_post_processing(self): 
        #get idx_lst and birth profile
        idx_lst = []
        for seed,idxs in self.tpmst_.connected_components_.items(): 
            idx_lst.append(idxs)
        mp = self.knn_.dists_[:,0].copy()
        mp = self._ktanh(mp,self.alpha,self.beta)
        self.post_processing_.fit(idx_lst,mp)

    def fit(self,signal:np.ndarray)->None: 
        """Fit PEPA
        
        Parameters
        ----------
        signal : numpy array of shape (n_samples, )
            The input samples (time series length).
        
        Returns
        -------
        self : object
            Fitted estimator.
        """
        self._base_persistence(signal)
        self._thresholds()
        self._birth_cut_dct()
        self._persistence_with_thresholds()

    def get_persistence(self,with_infinite_point = True)->np.ndarray: 
        pers = self.base_persistence_.get_persistence(with_infinite_point)
        if with_infinite_point:
            pers[-1,1] =0
            pers[-1,1] = np.max(pers[:,:-1])
        pers[:,:-1] = self._ktanh(pers[:,:-1],self.alpha,self.beta)
        return pers
    
    def plot_ktanh_distance(self):
        x = np.hstack((np.linspace(2,0,101)[:-1],np.linspace(0,2,100)))
        xticks_idx = np.hstack((np.arange(200)[::25],199))
        dist = self._ktanh(x,self.alpha,self.beta)

        fig,ax = plt.subplots(1,1,figsize = (5,5))
        ax.plot(x, label = "euclidean")
        ax.plot(dist, label = r"$Ktanh_{\alpha,\beta}$")
        ax.set_xticks(xticks_idx)
        ax.set_xticklabels(np.round(x[xticks_idx],1))
        ax.set_xlabel(r"$\|x-y\|_2$")
        ax.set_ylabel("distnace")
        ax.set_title(r"$\alpha:$" + f"{np.round(self.alpha,2)}   &   " + r"$\beta:$" + f"{np.round(self.beta,2)}")
        fig.tight_layout()
        plt.legend()
        plt.show()
  
        
    def plot_persistence_diagram(self): 
        pers = self.get_persistence(True)[:,:-1]
        pers = pers[pers[:,1]-pers[:,0]!=0]
        mask1 = pers[:,0]>self.b_cut_
        mask1 += (pers[:,0]<= self.b_cut_) * ((pers[:,1] - pers[:,0])<=self.p_cut_)
        mask2 = (pers[:,0]<= self.b_cut_) * ((pers[:,1] - pers[:,0])>self.p_cut_) 
        
        fig,ax = plt.subplots(1,1,figsize = (5,5))
        p0 = Polygon([[0,0],[2,0],[2,2]],color = 'grey', alpha=0.25)
        ax.add_patch(p0)
        ax.hlines(2,0,2,color="black", lw = 0.5,zorder=1)
        ax.hlines(0,0,2,color="black", lw = 0.5,zorder=1)
        ax.vlines(2,0,2,color="black", lw = 0.5,zorder=1)
        ax.vlines(0,0,2,color="black", lw = 0.5,zorder=1)
        ax.scatter(*pers[mask1].T, color = "tab:blue",zorder=2)
        ax.scatter(*pers[mask2].T, color = "tab:orange",zorder=2)
        ax.vlines(self.b_cut_,0,2,color="red",zorder=3)
        p2 = Polygon([[0,self.p_cut_],[2-self.p_cut_,2]], color = "red",zorder = 3)
        ax.add_patch(p2)
            
        fig.tight_layout()
        plt.show()
    
    def set_distance_params(self,alpha=None,beta=None): 
        if alpha is not None: 
            self.alpha = alpha
        if beta is not None: 
            self.beta = beta
        if (self.alpha is not None) * (self.beta is not None):
            self._thresholds()
            self._birth_cut_dct()
            self._persistence_with_thresholds()
        else: 
            raise ValueError("alpha or beta is None")

    def set_cut_values(self,p_cut=None,b_cut=None): 
        if p_cut is not None: 
            self.p_cut_ = p_cut
        if b_cut is not None: 
            self.b_cut_ = b_cut
        if (self.p_cut_ is not None) * (self.b_cut_ is not None): 
            self._birth_cut_dct()
            self._persistence_with_thresholds()
        else: 
            raise ValueError("p_cut or b_cut is None")
        
    @property
    def signal_(self): 
        return self.knn_.signal_
    
    @property
    def predictions_(self): 
        self._fit_post_processing()
        return self.post_processing_.predictions_
    
    @property
    def prediction_birth_list_(self):
        self._fit_post_processing()
        return self.post_processing_.prediction_birth_list_
    
    @property
    def prediction_mask_(self)->np.ndarray: 
        self._fit_post_processing()
        return self.post_processing_.prediction_mask_
    
#########################################################################################################################################
#########################################################################################################################################

