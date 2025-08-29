import numpy as np 
import plotly.graph_objects as go
import plotly.express as px
from scipy.interpolate import CubicSpline

##############################################################################################
##############################################################################################
### MOTIF ###
##############################################################################################
##############################################################################################

class Motif(object): 

    def __init__(self,length :int, amplitude :float, motif_fct : callable) -> None:
        """Motif initialization

        Args:
            length (int): Base motif length
            fundamental (float): fundamental frequence for the sum of waveform signal
            motif_fct (callable): function that generates pattern independently of fluctuations
        """
        self.length = length
        self.amplitude = amplitude
        self.motif_fct = motif_fct

    def _occurence_length(self, length_fluctuation = 0.): 
        if length_fluctuation !=0:
            time_offset = (2*np.random.rand(1)-1)*length_fluctuation 
        else: 
            time_offset = 0
        return time_offset
    
    def _occurence_amplitude(self, amplitude_fluctuation = 0.):
        if amplitude_fluctuation!=0: 
            amp = (2*np.random.rand(1)-1)*amplitude_fluctuation
        else: 
            amp = 0
        return amp

    def _time_amplitude(self,length_fluctuation = 0.,amplitude_fluctuation =0.):
        n_time = int((1+self._occurence_length(length_fluctuation))*self.length)
        time = np.linspace(0,1,n_time)
        amp = (1+self._occurence_amplitude(amplitude_fluctuation))*self.amplitude
        return time,amp
    
    def get_motif(self, length_fluctuation=0, amplitude_fluctuation=0):
        time, amp = self._time_amplitude(length_fluctuation,amplitude_fluctuation)
        return amp*self.motif_fct(time)


class Sin(Motif): 
    def __init__(self, length, fundamental, amplitude) -> None:
        self.fundamental = fundamental
        self.freq_ = (2*np.pi/length*np.arange(length)*fundamental).reshape(-1,1)
        self.offset_ = 2*np.pi*np.random.rand(length).reshape(-1,1)
        self.amp_ = ((2*np.random.rand(length)-1)*amplitude).reshape(-1,1)

        fct = lambda x : np.sum(self.amp_ * np.sin(self.freq_ * x + self.offset_),axis= 0)
        super().__init__(length, amplitude,fct)

class Cubic(Motif):
    def __init__(self, length, fundamental, amplitude) -> None:
        self.fundamental = fundamental
        x = np.linspace(0,1,fundamental+2)
        y = np.hstack((0,np.random.randn(fundamental),0))
        fct = CubicSpline(x,y)
        
        super().__init__(length, amplitude, fct)

##############################################################################################
##############################################################################################
### SIGNAL GENERATOR ###
##############################################################################################
##############################################################################################



class SignalGenerator(object): 
    """Synthetic signal generator.

    Parameters
    ----------
    n_motifs : int 
        Number of different motifs.
    motif_length : int or list of int, default=100
        Length(s) of the motifs to be generated.
        If an int is provided, it is interpreted as a constant length 
        used for all motifs (i.e., a list of length `n_motifs` filled with this value).
        If a list is provided, it should contain exactly `n_motifs` elements, 
        where each value specifies the length of a motif.
    motif_amplitude : float, optional (default = 1.0) 
        Base motifs amplitude.
    motif_fundamental : int, optional (default=1)
        Number of fundamental components used to construct the base motifs.
        A higher number results in more complex patterns.       
    motif_type : {'Sin', 'Cubic'}, optional, default="Sin"
        Type of motif to generate. 
        
        - "Sin": sinusoidal like patterns.
        - "Cubic": piecewise cubic patterns.
        
    noise_amplitude : float, optional(default=0.1) 
        Noise amplitude. The noise is gaussian of standard deviation `noise_amplitude`.
    n_novelties : int, optional (default=0)
        Number of novelties (i.e. motifs with only one occurence).
    length_fluctuation : float, optional (default=0.0)
        Percentage of fluctuation allowed in motif lengths, between 0.0 and 0.9.
        For each occurence, the actual motif length will be randomly chosen in the range 
        [`motif_length * (1 - length_fluctuation)`, `motif_length * (1 + length_fluctuation)`].
    amplitude_fluctuation : float, optional (default=0.0)
        Percentage of fluctuation allowed in motif amplitudes, between 0.0 and 0.9.
        For each occurence, the actual motif amplitude will be randomly chosen in the range 
        [`motif_amplitude * (1 - motif_fluctuation)`, `motif_amplitude * (1 + amplitude_fluctuation)`].
    sparsity : float, optional (default=0.2)
        Controls the spacing between motif occurrences, i.e., the proportion of motifless area between them.  
        The gap between motif occurences is set to `motif_length * sparsity`.
    sparsity_fluctuation : float, optional (default=0.0)
        Percentage of fluctuation allowed in the spacing between motif occurrences, between 0.0 and 0.9.  
        For each occurrence, the actual spacing will be randomly chosen in the range  
        [`motif_length * sparsity * (1 - sparsity_fluctuation)`, `motif_length * sparsity * (1 + sparsity_fluctuation)`].
    walk_amplitude : float,optional (default=0.0) 
        Amplitude of the random walk component.  
        The random walk is generated as the cumulative sum of a Gaussian noise process  
        with standard deviation equal to `walk_amplitude`.
    min_rep : int, optional (default=2)
        Minimum number of occurrences for each motif.  
        For each motif, the actual number of repetitions is randomly chosen in the range  
        [`min_rep`, `max_rep`].
    max_rep : int, optional (default=5)
        Maximum number of occurrences for each motif.  
        Used together with `min_rep` to define the range of possible repetitions per motif.
    exact_occurences : list of int, optional (default is None)
        Specifies the exact number of occurrences for each motif.  
        If provided, it must be a list of length `n_motifs`, where each value defines  
        the exact number of times the corresponding motif should appear.  
        This overrides the `min_rep` and `max_rep` parameters.
    exact_ts_length : int, optional (default is None) 
        If set, defines the exact total length of the generated time series.  
        Additional sparsity (i.e., motifless areas) will be uniformly added between motif occurrences  
        to match this target length.  
        If the base generated series (before adjustment) exceeds this value, an error is raised.
    
    Attributes
    ----------
    signal_ : np.ndarray of shape (n_samples,)
        The generated signal.
    labels_ : np.ndarray of shape (n_motifs, n_samples)
        Binary mask indicating the presence of motifs across the signal.  
        Each row corresponds to one motif, and each column to a time step.  
        A value of 1 means the motif is present at that time step, and 0 means it is not.
        """

    def __init__(self,n_motifs:int,motif_length=100,motif_amplitude=1,motif_fundamental =1,motif_type ='Sin',noise_amplitude=0.1,n_novelties=0,length_fluctuation=0.,amplitude_fluctuation=0.,sparsity=0.2,sparsity_fluctuation = 0.,walk_amplitude = 0.,min_rep=2,max_rep=5,exact_occurences=None,exact_ts_length=None) -> None:

        self.n_motifs = n_motifs
        self.motif_length = motif_length
        self.motif_amplitude = motif_amplitude
        self.motif_fundamental = motif_fundamental
        self.motif_type = motif_type
        self.noise_amplitude = noise_amplitude
        self.n_novelties = n_novelties
        self.length_fluctuation = length_fluctuation
        self.amplitude_fluctuation = amplitude_fluctuation
        self.sparsity = sparsity
        self.sparsity_fluctuation = sparsity_fluctuation
        self.walk_amplitude = walk_amplitude
        self.min_rep = min_rep
        self.max_rep = max_rep
        self.exact_occurences=exact_occurences
        self.n=exact_ts_length

    def _occurence(self): 
        if self.exact_occurences is None:
            lst = []
            for i in range(self.n_motifs): 
                lst.append(np.random.randint(self.min_rep,self.max_rep+1))
        else:
            lst=self.exact_occurences
        for i in range(self.n_novelties): 
            lst.append(1)
        self.occurences_ = np.array(lst).astype(int)
    
    def _ordering(self):
        arr = []
        for i,occ in enumerate(self.occurences_): 
            arr = np.r_[arr,np.full(occ,i)]
        np.random.shuffle(arr)
        self.ordering_ = arr.astype(int)

    def _motifs(self): 
        lst = []
        n_patterns = self.n_motifs+self.n_novelties
        #manage variability. 
        if isinstance(self.motif_length,int): 
            self.length_lst_ = (self.motif_length*np.ones(n_patterns)).astype(int)
        else: 
            self.length_lst_ = np.array(self.motif_length)
        if isinstance(self.motif_amplitude,int): 
            self.amplitude_lst_ = self.motif_amplitude*np.ones(n_patterns)
        else: 
            self.amplitude_lst_ = np.random.rand(n_patterns)*(self.motif_amplitude[1]-self.motif_amplitude[0]) + self.motif_amplitude[0]
        for m_len,m_amp in zip(self.length_lst_,self.amplitude_lst_): 
            lst.append(globals()[self.motif_type](m_len,self.motif_fundamental,m_amp))
        self.motifs_ = lst

    
    def generate(self): 
        """
        Generate a signal according to the initialization parameters.

        Returns
        -------
        signal_ : np.ndarray of shape (n_samples,)
            The generated signal.
        labels_ : np.ndarray of shape (n_motifs, n_samples)
            Binary mask indicating the presence of motifs across the signal.  
            Each row corresponds to one motif, and each column to a time step.  
            A value of 1 means the motif is present at that time step, and 0 means it is not.
        """
        self._occurence()
        self._ordering()
        self._motifs()
        #number of patterns
        n_patterns = self.n_motifs+self.n_novelties
        #Maximum length
        if isinstance(self.motif_length,int): 
            max_length = self.motif_length
        else: 
            max_length = self.motif_length[0]
        #signal initialisation
        sig = [np.zeros(max_length)]
        labels = [np.zeros((max_length,n_patterns))]
        pos_idx = max_length
        positions = {}
        for i in np.arange(n_patterns): 
            positions[i] = []
        #signal iteration
        for i,idx in enumerate(self.ordering_): 
            #add motif
            t_pattern = self.motifs_[idx].get_motif(self.length_fluctuation,self.amplitude_fluctuation)
            sig.append(t_pattern)
            t_label = np.zeros((t_pattern.shape[0],n_patterns))
            t_label[:,idx] = 1
            labels.append(t_label)
            positions[idx].append((pos_idx,t_pattern.shape[0]))
            pos_idx += t_pattern.shape[0]
            #add noise
            if i<len(self.ordering_): 
                max_sparsity = self.sparsity*max_length
                if max_sparsity>0:
                    if self.sparsity_fluctuation> 0:
                        length_sparsity = np.random.randint(max(0,int(max_sparsity*(1-self.sparsity_fluctuation))),int(max_sparsity*(1+self.sparsity_fluctuation)))
                    else: 
                        length_sparsity = int(max_sparsity)
                    sig.append(np.zeros(length_sparsity))
                    labels.append(np.zeros((length_sparsity,n_patterns)))
                    pos_idx += length_sparsity

        #postprocessing
        sig = np.hstack(sig)
        labels = np.vstack(labels).T
        #adding zeros to reach a given length if needed
        if self.n is not None: 
            missing_points=self.n-len(sig)-max_length
            if missing_points<0:
                print('signal is too short')
            else: 
                nb_zeros_by_seg=missing_points//(len(self.ordering_)-1)
                nb_zeros_end=missing_points%(len(self.ordering_)-1)+max_length
                for i,idx in enumerate(self.ordering_[:-1]):
                    n_idx=np.count_nonzero(self.ordering_[:i+1]==idx)-1
                    last_motif_end=positions[idx][n_idx][0]+positions[idx][n_idx][1]
                    sig=np.insert(sig,last_motif_end,np.zeros(nb_zeros_by_seg))
                    labels=np.insert(labels,last_motif_end,np.zeros((nb_zeros_by_seg,1)),axis=1)
                    idx_next_motif=self.ordering_[i+1]
                    n_idx_next_motif=np.count_nonzero(self.ordering_[:i+2]==idx_next_motif)-1
                    positions[idx_next_motif][n_idx_next_motif]=(positions[idx_next_motif][n_idx_next_motif][0]+(i+1)*nb_zeros_by_seg,positions[idx_next_motif][n_idx_next_motif][1])

                sig=np.concatenate((sig,np.zeros(nb_zeros_end)),axis=0)
                labels= np.concatenate((labels,np.zeros((n_patterns,nb_zeros_end))),axis=1)
        else:
            sig=np.concatenate((sig,np.zeros(max_length)))
            labels=np.concatenate((labels,np.zeros((n_patterns,max_length))),axis=1)

        #post processing
        #add noise
        sig += np.random.randn(sig.size)*self.noise_amplitude
        #add randown walk
        sig += np.cumsum(self.walk_amplitude*np.random.randn(sig.size))
        self.signal_ = sig
        self.labels_= labels
        self.positions_ = positions

        return self.signal_,self.labels_

    def plot(self, color_palette = 'Plotly'): 
        """ Plot the generated signal
        
        Parameters
        ----------
        color_palette : str, optional, default="Plotly"
            Color palette name from plotly.colors.qualitative. 
        Raises :
            Exception: Not enough color for the number of patterns.
        """
        palette = getattr(px.colors.qualitative,color_palette)
        n_patterns = self.n_motifs + self.n_novelties
        if len(palette) <= n_patterns+1:
            raise Exception('The color palette has not enough color. Please change color palette or reduce the number of patterns ')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(y = self.signal_, mode='lines', marker=dict(color = palette[0]),opacity =0.5,name = 'base signal',showlegend=False))
        for key,lst in self.positions_.items(): 
            for i,(start,length) in enumerate(lst): 
                time = np.arange(start, start+length)
                if key < self.n_motifs: 
                    name = f"motif {key}"
                else: 
                    name = f"novelty {key - self.n_motifs}"
                fig.add_trace(go.Scatter(x = time,y = self.signal_[time], mode='lines',marker = dict(color=palette[key+1]),name = name,legendgroup=str(key),showlegend= i==0))
        
        fig.update_layout(
            xaxis=dict(showgrid=False), 
            yaxis=dict(showgrid=False,zeroline=False),
            margin=dict(l=10, r=50, t=20, b=10),
            width = 1200, 
            height = 300
        )
        fig.show() 
