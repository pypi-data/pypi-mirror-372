import numpy as np
import tsmd.tools.distance as distance

class Valmod(object):
    """VALMOD algorithm for variable length motif discovery.

    Parameters
    ----------
    n_patterns : int 
        Number of patterns to detect.
    min_wlen : int 
        Minimum window length.
    max_wlen : int
        Maximum window length.
    p : int, optional (default=20) 
        Minimal number of distances computed in any cases.
    radius_ratio: float, optional (default=3)
        Threshold scaling factor for pattern inclusion. (Given a Motif Pair with distance d, the threshold is equal to radius_ratio*d)
    distance_name : str, optional, default="UnitEuclidean"
        Name of the distance.
    distance_params : dict, optional (default=dict())
        Additional distance parameters.

    Attributes
    ----------
    prediction_mask_ : np.ndarray of shape (n_patterns, n_samples)
        Binary mask indicating the presence of motifs across the signal.  
        Each row corresponds to one discovered motif, and each column to a time step.  
        A value of 1 means the motif is present at that time step, and 0 means it is not.
    """
    
    def __init__(self,n_patterns:int, min_wlen:int, max_wlen:int, p=20, radius_ratio=3, distance_name="UnitEuclidean", distance_params =dict())-> None:
        
        self.n_patterns = n_patterns
        self.min_wlen = min_wlen
        self.max_wlen = max_wlen+1
        self.p = p 
        self.radius_factor=radius_ratio
        self.distance_name = distance_name
        self.distance_params = distance_params

    def CompLB(self,idx:int,i:int)->np.ndarray:
        """Computes the lower bound of the distance between subsequence T[i, l+1] and all other subsequences T[j, l+1], for a given window length index.

        Parameters
        ----------
        idx : int
            Index of the window length (in `self.wlens_`).
        i : int 
            Index of the target subsequence.
        
        Returns
        -------
        LB : np.ndarray
            A 1D array containing the lower bounds of the distances between T[i, l+1] and each other valid subsequence, with `np.inf` for overlapping regions.
        """
        
        wlen=self.wlens_[idx]
        next_nDP=self.n-wlen
        next_non_overlap_mask=np.arange(max(0,i-wlen), min(next_nDP,i+wlen+1))
        #we compute qi,j for all j
        q=(self.distance_[idx].dot_product_/wlen -self.distance_[idx].means_[i]*self.distance_[idx].means_)/(self.distance_[idx].stds_[i]*self.distance_[idx].stds_)
        #we truncate it because for the next wlen we have less possible subsequences  
        q=q[:next_nDP]
        
        LB=np.zeros(next_nDP)
        mask=q<=0
        LB[mask]=np.sqrt(wlen)*(self.distance_[idx].stds_[:next_nDP][mask]/self.distance_[idx+1].stds_[mask])
        LB[~mask]=np.sqrt(wlen*(1-q[~mask]**2))*(self.distance_[idx].stds_[:next_nDP][~mask]/self.distance_[idx+1].stds_[~mask])

        LB[next_non_overlap_mask]=np.inf

        return LB
    
    def ComputeMatrixProfile(self,idx:int)-> tuple:
        """Computes the Matrix Profile and Lower Bound information for a given window length index.

        Parameters
        ----------
        idx : int
            Index of the window length to use (in `self.wlens_`).
        
        Returns
        -------
        MP : np.ndarray 
            The Matrix Profile, containing the minimal distances for each subsequence.
        IP : np.ndarray 
            The Index Profile, containing the indices of the nearest neighbors.
        listDP : list of np.ndarray 
            A list of `DP` objects (or named tuples) for each subsequence, each containing:
            
            - `idx_sort` (np.ndarray): Indices of the p smallest distances.
            - `trunc_dist` (np.ndarray): Corresponding distances.
            - `trunc_LB` (np.ndarray): Corresponding lower bounds.
            - `trunc_dot_prod` (np.ndarray): Corresponding dot products.
            
        """
        
        wlen=self.wlens_[idx]
        nDP=self.n-wlen+1
        MP=np.zeros(nDP)
        IP=np.zeros(nDP).astype(int)
        listDP=[]

        line=self.distance_[idx].first_line(0)
        non_overlap_mask = np.arange(0, min(nDP,wlen))
        line[non_overlap_mask] = np.inf
        MP[0]=np.min(line)
        IP[0]=np.argmin(line)
        #we don't need the lower bound for the last index 
        if idx+1< self.wlens_.shape[0]:
            LB=self.CompLB(idx,0)
            idx_sort=np.argsort(LB)[:self.p]
            trunc_dist=line[idx_sort]
            trunc_LB=LB[idx_sort]
            trunc_dot_prod=self.distance_[idx].dot_product_[idx_sort]

            listDP.append(DP(idx_sort, trunc_dist, trunc_LB, trunc_dot_prod))

        for i in range(1,nDP):
            line=self.distance_[idx].next_line()
            non_overlap_mask = np.arange(max(0,i-self.wlens_[idx]+1), min(nDP,i+wlen))
            line[non_overlap_mask] = np.inf
            MP[i]=np.min(line)
            IP[i]=np.argmin(line)
            #we don't need the lower bound for the last index 
            if idx+1< self.wlens_.shape[0]:
                LB=self.CompLB(idx,i)
                idx_sort=np.argsort(LB)[:self.p]
                trunc_dist=line[idx_sort]
                trunc_LB=LB[idx_sort]
                trunc_dot_prod=self.distance_[idx].dot_product_[idx_sort]
                    
                listDP.append(DP(idx_sort, trunc_dist, trunc_LB, trunc_dot_prod))

        return MP, IP, listDP


    def updateDistAndLB(self, idx:int, i:int, j:int,dot_product:np.ndarray, LB:np.ndarray)-> tuple:
        """Updates the distance and lower bound between two subsequences when increasing the window length.

        This method is used to incrementally compute the distance `D[i,j]` and the lower bound `LB[i,j]`
        for a longer window (length `l+1`) based on the values computed at length `l`.
        It also updates the dot product accordingly.

            
        Parameters
        ----------
        idx : int 
            Index of the current window length in `self.wlens_`.
        i : int 
            Index of the first subsequence (unknown `T[i, l+1]`).        
        j : int 
            Index of the second subsequence (known `T[j, l+1]`).
        dot_product : np.ndarray 
            Dot product between subsequences at length `l`.
        LB : np.ndarray
            Lower bound between subsequences at length `l`.
            
        Returns
        -------
        new_distance : np.ndarray 
            Updated distance between `T[i, l+1]` and `T[j, l+1]`.
        new_LB : np.ndarray
            Updated lower bound values. 
        new_dot_product : np.ndarray 
            Updated dot product for window length `l+1`.
        
        """
        
        wlen=self.wlens_[idx]
        newlen=wlen+1
        new_dot_product=dot_product+self.signal_[i+newlen-1]*self.signal_[j+newlen-1]
        #we check if the increase of the length don't create an overlap
        
        if np.abs(i-j)<newlen:
            new_dist=np.inf
            new_LB=np.inf
        else:    
            new_dist=(new_dot_product-newlen*self.distance_[idx+1].means_[i]*self.distance_[idx+1].means_[j])/(newlen*self.distance_[idx+1].stds_[i]*newlen*self.distance_[idx+1].stds_[j])
            new_dist= np.sqrt(np.clip(2*(1-new_dist),0,None))
        
            new_LB= LB * self.distance_[idx].stds_[j]/self.distance_[idx+1].stds_[j]

        return new_dist, new_LB, new_dot_product
 
    def ComputeSubMP(self,idx:int)->tuple:
        """Compute the SubMatrixProfile of window length `l+1` based on the current profile of length `l`.
            
        Parameters
        ----------
        idx : int 
            Index of the current window length in `self.wlens_`.
                
        Returns
        -------
        bBestM : Bool
            True if the SubMatrixProfile is sufficient to reconstruct the full MatrixProfile of length `l+1`, 
            False otherwise (i.e., additional distances need to be computed).
        SubMP : np.ndarray 
            The computed SubMatrixProfile.
        IP : np.ndarray 
            The index profile associated with `SubMP`. Each entry corresponds to the index of the best match 
            (i.e., the subsequence with the minimum distance).
        """
        
        wlen=self.wlens_[idx]
        next_nDP=self.n-wlen
        SubMP=np.zeros(next_nDP)
        SubIP = np.zeros(next_nDP).astype(int)
        minDistAbs, minLBAbs = np.inf, np.inf
        nonValidDP=[]
        for j in range(next_nDP):
            minDist = np.inf
            DP_iter=self.listDP[j]
            #the maximum LB is at the last position
            maxLB=DP_iter.LB[-1]
            for e in range(self.p):
                i=DP_iter.idxs[e]
                if i<next_nDP:
                    #it's possible to have i>=next_nDP if we have not compute complete matrix profiles for a long time
                    dot_product=DP_iter.dot_product[e]
                    LB=DP_iter.LB[e]
                    e_dist, e_LB, e_dot_product = self.updateDistAndLB(idx,i,j,dot_product,LB)   
                    DP_iter.distance[e], DP_iter.LB[e], DP_iter.dot_product[e] = e_dist, e_LB, e_dot_product
                    minDist=min(minDist,e_dist)
                    if minDist==e_dist:
                        ind=i
            #we update DP
            self.listDP[j]=DP_iter
            if minDist<maxLB:
                minDistAbs=min(minDistAbs,minDist)
                SubMP[j]=minDist
                SubIP[j]=ind
            else:
                minLBAbs=min(minLBAbs,maxLB)
                SubMP[j]=np.inf
                nonValidDP.append([j,maxLB])
                
                
        bBestM=minDistAbs<minLBAbs
        
        if (not bBestM) and len(nonValidDP)<(next_nDP*np.log(self.p)/np.log(next_nDP)):
            for ind,maxLB in nonValidDP:
                if maxLB<minDistAbs:
                    
                    line=self.distance_[idx+1].first_line(ind)
                    non_overlap_mask = np.arange(max(0,ind-self.wlens_[idx+1]+1), min(next_nDP,ind+wlen+1))
                    line[non_overlap_mask]=np.inf
                    SubIP[ind]=np.argmin(line)
                    SubMP[ind]=np.min(line)
                    
                    if idx+2< self.wlens_.shape[0]:
                        LB=self.CompLB(idx+1,ind)
                        
                        idx_sort=np.argsort(LB)[:self.p]
                        trunc_dist=line[idx_sort]
                        trunc_LB=LB[idx_sort]
                        trunc_dot_prod=self.distance_[idx+1].dot_product_[idx_sort]
                        
                        self.listDP[ind]=(DP(idx_sort, trunc_dist, trunc_LB, trunc_dot_prod))
                    
            bBestM=True

        return bBestM,SubMP, SubIP

        
    def Valmod(self):
        """Compute the Variable length matrix profile (VALMP)
        """

        MP, IP, self.listDP = self.ComputeMatrixProfile(0)
        nDP=self.n-self.min_wlen+1
        self.VALMP = VALMP(nDP)
        self.bestKpairs=self.VALMP.updateVALMPForMotifSets(MP,IP,self.min_wlen,self.listDP)

        for idx,wlen in enumerate(self.wlens_[:-2]):
            new_nDP= self.n-wlen
            self.VALMP.nDP=new_nDP
            bBestM, SubMP, SubIP = self.ComputeSubMP(idx)
            if bBestM:
                self.bestKpairs=self.VALMP.updateVALMPForMotifSets(SubMP,SubIP,wlen+1,self.listDP)
            else:
                MP, IP, self.listDP = self.ComputeMatrixProfile(idx+1)
                self.bestKpairs=self.VALMP.updateVALMPForMotifSets(MP, IP, wlen+1,self.listDP)

    def remove_trivial_matches(self,idxs,len):
        idxs_copy=np.copy(idxs)
        i=0
        while i < idxs_copy.shape[0]-1:
            idxs_to_remove=[]
            for j in range(i+1,idxs_copy.shape[0]):
                if np.abs(idxs_copy[i]-idxs_copy[j])<len:
                    idxs_to_remove.append(j)
            idxs_copy=np.delete(idxs_copy,idxs_to_remove)
            i+=1
        return idxs_copy

    def computeVarLengthMotifSets(self):
        non_overlap_mask=np.zeros(self.n-self.min_wlen+1).astype(bool)
        self.motifs=[]
        for pair in self.bestKpairs:
            #if we already have the right number of motifs we stop
            if len(self.motifs)>=self.n_patterns:
                break 
            #we check if we have an overlap with an already existing motif
            if any(non_overlap_mask[pair.off1:pair.off1+pair.wlen]) or any(non_overlap_mask[pair.off2:pair.off2+pair.wlen]):
                continue
            r = self.radius_factor * pair.distance
            #maxLB1= max(pair.partDP1.distance)
            #maxLB2= max(pair.partDP2.distance)
            #if maxLB1 > r:
            #    print('1')
            #    idxs_to_keep_1=pair.partDP1.idxs[pair.partDP1.distance<=r]
            #else:
            l_idx=np.where(self.wlens_==pair.wlen)[0][0]
            line=self.distance_[l_idx].first_line(pair.off1)
            #we normalize the line
            line/=np.sqrt(pair.wlen)
            idxs_to_keep_1=np.where(line<=r)[0]
            #if maxLB2 > r:
            #    print('2')
            #    idxs_to_keep_2=pair.partDP2.idxs[pair.partDP2.distance<=r]
            #else:
            l_idx=np.where(self.wlens_==pair.wlen)[0][0]
            line=self.distance_[l_idx].first_line(pair.off2)
            idxs_to_keep_2=np.where(line<=r)[0]
            idxs=np.concatenate(([pair.off1],[pair.off2],idxs_to_keep_1,idxs_to_keep_2))
            #we start by removing the indexes that overlap with already existing motifs
            new_idxs=[]
            for idx in idxs:
                if not any(non_overlap_mask[idx:idx+pair.wlen]) and idx+pair.wlen<non_overlap_mask.shape[0]:
                    new_idxs.append(idx)
            #then we remove trivial matches
            new_idxs=self.remove_trivial_matches(new_idxs,pair.wlen)
            #we update the motif list and the mask 
            new_motif=[]
            for idx in new_idxs:
                occurence=np.arange(idx,idx+pair.wlen)
                non_overlap_mask[occurence]=1
                new_motif.append(occurence)
            self.motifs.append(new_motif)

    def fit(self,signal):
        """Fit VALMOD
        
        Parameters
        ----------
        signal : numpy array of shape (n_samples, )
            The input samples (time series length).
        
        Returns
        -------
        self : object
            Fitted estimator.
        """
        
        self.signal_=signal
        self.n=self.signal_.shape[0]
        self.distance_=[]
        self.wlens_ = np.arange(self.min_wlen,self.max_wlen+1)
        for idx,wlen in enumerate(self.wlens_):
            self.distance_.append(getattr(distance,self.distance_name)(wlen,**self.distance_params))
            self.distance_[idx].fit(self.signal_)
        self.bestKpairs=[]
        self.Valmod()
        self.bestKpairs.sort(key=Pair.get_distance)
        self.computeVarLengthMotifSets()

    @property
    def prediction_mask_(self):
        mask=np.zeros((self.n_patterns,self.signal_.shape[0]))
        for i in range(len(self.motifs)):
            motif=self.motifs[i]
            for sub_motif in motif:
                mask[i,sub_motif]=1
        #remove null lines
        mask=mask[~np.all(mask == 0, axis=1)]
        return mask

class VALMP(object):
    def __init__(self, nDP:int) -> None:
        """Initialization
            Args: nDP = initial number of subsequences
        """
        
        self.nDP = nDP
        self.distances = np.inf * np.ones(self.nDP)
        self.normDistances = np.inf * np.ones(self.nDP)
        self.bestKpairs= [0]*self.nDP
        self.lengths = np.zeros(self.nDP)
        self.indices = np.zeros(self.nDP)

    def updateVALMPForMotifSets(self,MPnew:np.ndarray, IP:np.ndarray, wlen:int,listDP) -> None:
        """Update of VALMP
        
        Parameters
        ----------
        MPnew : np.ndarray 
            Matrix profile for the current length.
        IP : np.ndarray
            Index profile for the current length.
        wlen : int
            Current length.

        Returns
        -------
        bestKpairs : array of Pair
            Array containing the best motif pairs.
        """
        
        lNormDist = MPnew / np.sqrt(wlen)
        for i in range(self.nDP):
            if lNormDist[i] < self.normDistances[i]:
                new_pair=Pair(i,IP[i],lNormDist[i],wlen,listDP[i],listDP[IP[i]])
                self.bestKpairs[i]=new_pair
                self.distances[i]=MPnew[i]
                self.normDistances[i]=lNormDist[i]
                self.lengths[i] = wlen
                self.indices[i] = IP[i]
        
        return self.bestKpairs
    
class DP(object):
    
    def __init__(self, idxs:np.ndarray, distance:np.ndarray, LB:np.ndarray, dot_product:np.ndarray )-> None:

        self.idxs = idxs
        self.distance = distance
        self.LB = LB
        self.dot_product =dot_product
        
class Pair(object):

    def __init__(self,off1,off2,distance,wlen,partDP1,partDP2):
        
        self.off1=off1
        self.off2=off2
        self.distance=distance
        self.wlen=wlen
        self.partDP1=partDP1
        self.partDP2=partDP2

    def get_distance(self):

        return self.distance
