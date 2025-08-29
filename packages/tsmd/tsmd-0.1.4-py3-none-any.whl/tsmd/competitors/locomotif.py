import tsmd.competitors.competitors_tools.locomotif_original_tools as loctools
import numpy as np

class LocoMotif:
    """LoCoMotif algorithm for motif discovery.

    Parameters
    ----------
    min_wlen : int
        Minimium window length.
    max_wlen : int 
        Maximum window length.
    n_patterns : int, optional (default is None) 
        Maximum number of motif sets to find. If None, the number of patterns is inferred. 
    rho: float, optional (default=0.8)
        The strictness parameter between 0 and 1. It is the quantile of the similarity matrix to use as the threshold for the LoCo algorithm.
    overlap : float, optional (default=0.0)
        Defines the maximal amount of overlap between subsequences accepted.
    start_mask : np.ndarray, optional (default is None)
        Mask for the starting time points of representative motifs, where True means allowed. If None, all points are allowed.
    start_mask : np.ndarray, optional (default is None)
        Mask for the ending time points of representative motifs, where True means allowed. If None, all points are allowed.
    warping : bool, optional (default=True)
        Whether warping is allowed (True) or not (False).
    
    Attributes
    ----------
    prediction_mask_ : np.ndarray of shape (n_patterns, n_samples)
        Binary mask indicating the presence of motifs across the signal.  
        Each row corresponds to one discovered motif, and each column to a time step.  
        A value of 1 means the motif is present at that time step, and 0 means it is not.
        """


    def __init__(self, min_wlen, max_wlen, rho=0.8,  n_patterns=None, start_mask=None, end_mask=None, overlap=0, warping=True):
        self.rho=rho
        self.l_min=min_wlen
        self.l_max=max_wlen
        self.nb=n_patterns
        self.start_mask=start_mask
        self.end_mask=end_mask
        self.overlap=overlap
        self.warping=warping

    def fit(self,signal):
        """Fit LoCoMotif
        
        Parameters
        ----------
        signal : numpy array of shape (n_samples, )
            The input samples (time series length).
        
        Returns
        -------
        self : object
            Fitted estimator.
        """
        self.signal=signal
        self.n=self.signal.shape[0]
        self.motif_sets=loctools.apply_locomotif(signal,self.rho,self.l_min,self.l_max,self.nb,self.start_mask,self.end_mask,self.overlap,self.warping)

    @property
    def prediction_mask_(self):
        nb_motifs=len(self.motif_sets)
        mask=np.zeros((nb_motifs,self.n))
        for i in range(nb_motifs):
            for occurence_s,occurence_e in self.motif_sets[i]:
                mask[i,occurence_s:occurence_e]=1
        return mask
        
