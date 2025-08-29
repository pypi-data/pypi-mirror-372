
import numpy as np
from pathlib import Path
import subprocess 
import os

import warnings
warnings.filterwarnings('ignore')

class Grammarviz(object): 
    """Grammarviz algorithm for motif discovery.

        Parameters
        ----------
        n_patterns : int 
            Number of patterns.
        alphabet_size : int, optional (default=5)
            Alphabet size for the discretization of the time series.
        numerosity : str, optional (default to "MINDIST")
            Numerosity reduction type.
        window_size : int, optional (default=30)
            Window_size.
        word_size : int, optional (default=10)
            Word size.
        Attributes
        ----------
        prediction_mask_ : np.ndarray of shape (n_patterns, n_samples)
            Binary mask indicating the presence of motifs across the signal.  
            Each row corresponds to one discovered motif, and each column to a time step.  
            A value of 1 means the motif is present at that time step, and 0 means it is not.
            """
    def __init__(self,n_patterns:int,alphabet_size=5,numerosity="MINDIST",window_size = 30,word_size = 10,folder_java = "./competitors/competitors_tools/grammarviz",file_exchange_location="target/file_exchange") -> None:
        
        self.n_cluster = n_patterns
        self.alphabet_size = alphabet_size
        self.numerosity = numerosity
        self.window_size = window_size
        self.word_size = word_size
        self.folder_java = Path(folder_java)
        self.file_exchange_location = Path(file_exchange_location)

    def fit(self,signal:np.ndarray)->None:
        """Fit Grammarviz
        
        Parameters
        ----------
        signal : numpy array of shape (n_samples, )
            The input samples (time series length).
        
        Returns
        -------
        self : object
            Fitted estimator.
        """
        self.signal_length = signal.shape[0]
        #prepare data
        self.data_path_= self.file_exchange_location/"data.txt"
        try: 
            os.remove(self.folder_java/self.data_path_)
        except: 
            pass
        self.output_path_ = self.file_exchange_location/"output.txt"
        try: 
            os.remove(self.folder_java/self.output_path_)
        except: 
            pass

        np.savetxt(self.folder_java/self.data_path_,signal)

        #Execute algorithm: 
        command = f"java -cp \"target/grammarviz2-1.0.1-SNAPSHOT-jar-with-dependencies.jar\" net.seninp.grammarviz.cli.TS2SequiturGrammar -d target/file_exchange/data.txt -o target/file_exchange/output.txt -a {self.alphabet_size} -p {self.word_size} -w {self.window_size} --strategy {self.numerosity}"
        subprocess.run([command],shell=True,cwd = self.folder_java/"",stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)

        #read output
        self.prediction_mask_ = self._read_grammaviz_result()
        #remove null lines
        self.prediction_mask_ = self.prediction_mask_[~np.all(self.prediction_mask_ == 0, axis=1)]

        os.remove(self.folder_java/self.data_path_)
        os.remove(self.folder_java/self.output_path_)
        
        return self

    def _read_grammaviz_result(self)->np.ndarray:
        """Read output txt file to compute the mask

        Returns:
            np.ndarray: reccurent pattern prediction mask.
        """

        with open(self.folder_java/self.output_path_,"r") as f: 
            res = f.read()

        r0 = res.split("///")[1]
        r0 = r0.split("\n")[1]
        r0 = r0.split(",")[0]
        r0 = r0.split("-> ")[1]
        r0 = r0.replace(" ", ",")
        r0 = r0[1:-1]
        r0 = r0.split(",")
        rlabels, rcounts = np.unique(r0,return_counts=True)
        ridxs = np.array([i for i,r in enumerate(rlabels) if r[0]=="R"])
        if len(ridxs)>0:
            rlabels = rlabels[ridxs]
            rcounts = rcounts[ridxs]
            n_rules = ridxs.shape[0]
            counts = 0
            idxs = []

            while (counts < min(self.n_cluster,n_rules)): 
                idx = np.argmax(rcounts)
                idxs.append(idx)
                rcounts[idx] = 0
                counts +=1 

            idxs = [int(r[1:])-1 for r in rlabels[idxs]]

            res = res.split("///")[2:]
            mask = np.zeros((min(self.n_cluster,n_rules),self.signal_length))

            for i,motif in enumerate(np.array(res)[idxs]): 
                motif = motif.split("\n")
                starts = motif[2].split(":")[-1][1:]
                starts = starts.strip('][').split(', ')
                starts = np.array(starts).astype(int)
                lengths = motif[3].split(":")[-1][1:]
                lengths = lengths.strip('][').split(', ')
                lengths = np.array(lengths).astype(int)
                overlaps = np.clip(np.hstack(((starts+lengths)[:-1]-starts[1:],0)),0,np.inf).astype(int)
                for idx,wlen,ovl in zip(starts,lengths,overlaps): 
                    mask[i,idx:idx+wlen-ovl-1] = 1
        else: 
            mask = np.zeros((self.n_cluster,self.signal_length))
        
        return mask