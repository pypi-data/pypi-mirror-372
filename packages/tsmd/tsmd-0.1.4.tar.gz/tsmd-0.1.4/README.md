<p align="center">
<img width="200" src="./assets/TSMD.png"/>
</p>
<h1 align="center">TSMD</h1>
<h2 align="center">Time Series Motif Discovery</h2>

<p align="center">
<img alt="PyPI - Downloads" src="https://pepy.tech/badge/tsmd"> <img alt="PyPI" src="https://img.shields.io/pypi/v/tsmd"> <img alt="License" src="https://img.shields.io/github/license/grrvlr/TSMD"> <img alt="GitHub issues" src="https://img.shields.io/github/issues/grrvlr/TSMD"> <img alt="ReadTheDocs Status" src="https://readthedocs.org/projects/tsmd/badge/?version=latest"> 
</p>

Motif Discovery consists of identifying repeated patterns and locating their occurrences in a time series without prior knowledge about their shape or location. In practice, motif discovery faces several data-related challenges which has led to numerous definitions of the motif discovery problem and algorithms partially encompassing these challenges. In this repo, we provide an exhaustive review of the literature in terms of data-related challenges, motif definitions, and algorithms. We also present an analysis of strengths and weaknesses of algorithms carefully chosen to best represent the literature spectrum. The analysis follows research questions we identified from our review. Our experimental results provide practical guidelines for selecting motif discovery algorithms suitable for the task at hand and open to new research directions. Overall, we provide implementation of the main motif discovery methods proposed in the literature and the experimental scripts to compare them in terms of accuracy and execution time.

## License

The project is licensed under the *MIT License*: <https://mit-license.org>.

If you use TSMD in your project or research, please cite the following paper:

   Time Series Motif Discovery: A Comprehensive Evaluation
   Valerio Guerrini, Thibaut Germain, Charles Truong, Laurent Oudre, Paul Boniol.
   Proceedings of the VLDB Endowment (PVLDB 2025) Journal, Volume 18.

You can use the following BibTeX entries:

```bibtex
@article{Guerrini2025tsmd,
   title={Time Series Motif Discovery: A Comprehensive Evaluation},
   author={Guerrini, Valerio and Germain, Thibaut and Truong, Charles and Oudre, Laurent and Boniol, Paul},
   journal={Proceedings of the VLDB Endowment},
   volume={18},
   number={7},
   year={2025},
   publisher={VLDB Endowment}
}
```

## Contributors

* Valerio Guerrini (Centre Borelli)
* Thibaut Germain (Centre Borelli)
* Charles Truong (Centre Borelli)
* Laurent Oudre (Centre Borelli)
* Paul Boniol (Inria, ENS)

## Installation

We provide below some important guidelines to use our datasets or implemented algorithms.

### 1. Install TSMD with pip

You can install TSMD using pip:

```bash
pip install tsmd
```

### 2. Install tsmd from source: 

The following tools are required to install TSMD from source:

- git
- conda (anaconda or miniconda)


Clone this `repository <https://github.com/grrvlr/TSMD.git>`_ using git and go into its root directory.

```bash

   git clone https://github.com/grrvlr/TSMD.git
   cd TSMD/
```
Create and activate a conda-environment 'TSMD'.

```bash

   conda env create --file environment.yml
   conda activate TSMD
```

For more details on documentation, please see <https://tsmd.readthedocs.io/en/latest/index.html>.

## Time series Datasets for Motif Discovery

First, due to limitations in the upload size on GitHub, we host the datasets at a different location. Please download the datasets using the following links:
- Real time series Collection: https://kiwi.cmla.ens-cachan.fr/index.php/s/MwbqcKBdp2ZGzTx

Overall, our benchmark consider both real time series collection and a synthetic generator to evaluate specific parameters and characteristics. In total, we have the following datasets:

| Dataset                 | # TS | TS len. | # motifs | # motifs per TS  | ratio motif | avg. Motif len. | intra Motif len. (std) | Inter M.otif len.(std) |
|-------------------------|------|---------|----------|------------------|-------------|-----------------|------------------------|------------------------|
| arm-CODA                | 64   | 8,050   | 7        | 5                | 0.65        | 520             | 22                     | 88         |
| mitdb                   | 100  | 20,000  | 10       | 1.6              | 0.99        | 281             | 36                     | 10         |
| mitdb1                  | 100  | 20,000  | 1        | 1                | 0.98        | 320             | 12                     | 0          |
| ptt-ppg                 | 100  | 20,000  | 1        | 1                | 0.98        | 324             | 15                     | 0          |
| REFIT                   | 100  | 210,870 | 3        | 2.2              | 0.08        | 410             | 13                     | 34         |
| SIGN                    | 50   | 172,780 | 3        | 3                | 0.10        | 74              | 34                     | 3          |
| JIGSAWMaster            | 23   | 10,300  | 8        | 3.8              | 0.66        | 156             | 38                     | 66         |
| JIGSAWSlave             | 32   | 10,160  | 9        | 3.9              | 0.65        | 146             | 35                     | 60         |


### arm-CODA 

It is a dataset of 240 multivariate time series collected using 34 Cartesian Optoelectronic Dynamic Anthropometers (CODA) placed on the upper limbs of 16 healthy subjects, each of whom performed 15 predefined movements. Each sensor records its position in 3D space. To construct the dataset, we kept the left forearm sensor of ID 29 and 5 of the predefined movements. The occurrences of the five movements were randomly placed along the time axis for each subject, sensor, and dimension. Gaussian noise with a signal-to-noise ratio of 0.01 is added to all time series. This resulted in a dataset of 64 univariate time series.

### mitdb1 

The MIT-BIH Arrhythmia Database contains 48 half-hour recordings of two-channel ambulatory electrocardiograms (ECGs) sampled at 360Hz. Cardiologists annotated the heartbeats according to 19 categories. We divide all recordings into a time series of 1 minute and keep only the first channel. We selected time series of healthy subjects that contains only normal heartbeats and randomly selected 100 time series.

### mitdb: 

We randomly selected 100 one-minute time series from the MIT-BIH dataset (healthy subjects or not). Each time series has 1 to 4 motifs (normal heartbeats and different types of arrhythmia), each with several occurrences.

### ptt-ppg 

Pule-Transit-Time photoplethysmogram (PPG) dataset consists of time series recorded with multiple sensors (sampled at 500Hz) from healthy subjects performing physical activities. The annotated motifs are heartbeats. We randomly select 100 40-second-long signals from the first channel of the PPG during the “run” activity.

### REFIT: 

This dataset provides aggregate and individual appliance load curves at 8-second sampling intervals from 20 houses. We selected 10 houses and aggregated recordings of the appliances available: dishwasher, washing machine, and tumble dryer. The recordings were down-sampled to 32-second intervals and divided into time series of one week. We kept 10 time series for each house in which the appliances were not used simultaneously. It resulted in a 100 univariate time series dataset with a maximum of 3 different motifs.

### SIGN: 

This dataset is built from samples of Auslan (Australian Sign Language) signs. 95 signs were collected from five signers, totaling 6650 sign samples. Based on this, we generate a long time series by injecting several words (concatenation of signs). The different injected signs are the motifs. Every word is separated with flat sequences (i.e., without any motifs). In total, we generate 50 different time series.

### JIGSAW 

The time series of this dataset are recorded from the DaVinci Surgical System. Each time series contains 76 dimensions. Each dimension corresponds to a sensor
(with an acquisition rate of 30 Hz). The sensors are divided into two groups: patient-side manipulators (**JIGSAWSlave**), and master tool manipulators (**JIGSAWMaster**). The recorded time series corresponds to surgeons performing a suture that can be decomposed into 11 gestures. Each gesture corresponds to a motif that can be repeated multiple times within the same time series. Overall, we selected 23 time series (from different sensors) for JIGSAWMaster and 32 time series for JIGSAWSlave.

### Synthetic generator

For a given number of motifs $K$, the generator constructs one representative per motif. Given an average length $l_i$, and a fundamental frequency (set to 4Hz in our case), a motif representative is generated as the sum of the sine function of the $l_i$ first harmonics, with the phases and the amplitudes uniformly sampled over $[−\pi, \pi]$ and $[−1, 1]$. The $k_i$ occurrences of motif $i$ are then constructed by temporally distorting the initial representative. In practice, we use a parameter called \textit{length fluctuation} defined as the maximum variability of the occurrence's length to the average length. For example, a ratio of 0.1 means that we resample the occurrences of the motif so they have lengths varying up to $\pm 10 \%$ from the average length. The occurrences of all motifs are then randomly concatenated and spaced according to sparsity parameters. Finally, white Gaussian noise of standard deviation $\sigma$, and a random walk (to model local linear trends) are added to the signal.

## Motif Discovery Methods

In order to address the research questions enumerated in the previous section, we have to carefully select algorithms  from different families to best represent the diversity of Motif Discovery techniques. We provide below a taxonomy of methods proposed in the literature. Among all methods listed in this taxonomy, we selected 11 Motif Discovery algorithms.

<p align="center">
<img width="900" src="./assets/Taxonomy_TSMD.png"/>
</p>

The following motivations drive our selection of Motif Discovery methods: 
1. Our collection of methods should have at least one representative from each of the main families of methods we presented earlier. 
2. Priority is given to methods that have represented a great advance in the field.
3. Our collection should contain recent approaches tackling a large panel of challenges.
4. We finally favor algorithms for which implementation was proposed, or the code description was detailed enough.

These criteria led us to choose the following methods: 

| Methods               | family | Parameters | Complexity (Worst Case) |
|-----------------|----------------------------|----------------------------------------|--------------------------------------------------------|
| SetFinder       |  Frequency                 | $K,w,R$                                | $O(n^3)$                                               |
| LatentMotif     |  Frequency                 | $K,w,R$                                | $O(wn)$                                                |
| STOMP           |  Similarity                | $K,w,r$                                | $O(n^2)$                                               |
| VALMOD          |  Similarity                | $K,w_{\min},w_{\max},r$                | $O((w_{\max} - w_{\min})n^2)$                          |
| PanMP           |  Similarity                | $K, w_{\min},w_{\max}, r$              | $O((w_{\max} - w_{\min})n^2)$                          |
| $k$-Motiflets   |  Similarity                | $k_{\max},w_{\min},w_{\max}$           | $O(k_{\max}n^2 + nk_{\max}^2)$                         |
| PEPA            |  Similarity                | $w_{\min},K$                           | $O(Kn^2)$                                              |
| A-PEPA          |  Similarity                | $w_{\min}$                             | $O(Kn^2)$                                              |
| GrammarViz      |  Encoding                  | $K,w$                                  | $O(wn^2)$                                              |
| MDL-Clust       |  Encoding                  | $w_{\min}, w_{\max}$                   | $O(n^3/w_{min} + (w_{max} - w_{min})n^2 )^*$           |
| LoCoMotif       |  Encoding                  | $K,w_{\min},w_{\max}$                  | $O(n^2\frac{w_{\max} - w_{\min}}{w_{\min}})$           |


### SetFinder 

This algorithm finds the K-motif sets directly, based on a counting and separating principle. In practice, each subsequence is compared to every other, and the non-overlapping matches  are counted. Then, each subsequence with a non-zero count is checked to ensure that its distance to another subsequence with a larger number of matches is greater than a given threshold.

### LatentMotif 

This method addresses a variant of the K-Motifs problem as a constrained optimization task, where the center of the motif is learned (the center doesn't need to be a subsequence of $S$ but can belong to any element in $\mathbb{R}^n$). The initial objective and constraint functions are regularized to enable gradient ascent. The learned subsequences are then returned as the centers of the motif sets. To identify all occurrences of each motif set, a complete scan of the time series subsequences is conducted. Non-overlapping subsequences within a distance $R$ of the learned center are considered occurrences of the motif set.


### STOMP
The STOMP algorithm is a similarity-based method and proposes a fast computation of the Matrix Profile by efficiently leveraging the Fast Fourier Transform (FFT). Once the  Matrix Profile is computed, the center of the Motif Set is defined as the subsequence with the minimum distance to another non-overlapping subsequence. A full scan of the time-series subsequences is performed, and non-overlapping subsequences that are at a distance of less than $R$ from the center are identified as occurrences of the corresponding Motif set.

### PanMP 

PanMP aims to generalize the Matrix Profile approach to detect patterns at varying time scales without requiring prior knowledge of the Motif size. To achieve this, the PanMatrixProfile—a matrix that contains Matrix Profiles for a range of window lengths in a time series—is computed. Based on distance and regardless of window size, the best non-overlapping Motif Pairs are then iteratively selected. The Motif sets are constructed from these selected Motif Pairs in the same way as in STOMP. Note that if the range of window sizes is restricted to a single value, this method functions identically to STOMP.

### VALMOD 

VALMOD has a similar goal to PanMP but employs a slightly different approach. It leverages pruning techniques to compute the Matrix Profile over a range of window lengths, $\ell$. Motif Pairs are iteratively selected based on distance normalized by the square root of the window length. Motif sets are then built from these top Motif Pairs by identifying non-overlapping subsequences within a distance $< R$ from one of the two centers. 

### $k$-Motiflets 

Unlike most other algorithms in our benchmark that require the user to set a radius parameter $R$, the k-Motiflets method aims to discover motifs without needing this parameter. Instead, the user specifies the desired number of occurrences $k$ for the target motif. With $k$ defined, the method identifies the set of $k$ non-overlapping subsequences with minimal extent, where extent is the maximum pairwise distance among elements in the set.


### PEPA

This method extracts the motifs through three computational steps: (i) the time series is transformed into a graph with nodes representing subsequences and edges weighted by the distance between subsequences; (ii) persistent homology is applied to detect significant clusters of nodes, isolating them from nodes that correspond to irrelevant parts of the time series; and (iii) a post-processing step merges temporally adjacent subsequences within each cluster to form variable length motif sets. Note also that this method utilizes the LT-Normalized Euclidean distance, a distance measure invariant to linear trends.

### A-PEPA 

A variant of PEPA that does not require the user to define the exact number of motif sets and estimates it automatically.

### Grammarviz 

Grammarviz uses grammar induction methods for motif detection. In practice, the time series is discretized using SAX, and grammar induction techniques, such as Sequitur or RE-PAIR, are applied to the discretized series to identify grammar rules. The most frequent and representative grammar rules are selected, and occurrences of the various motifs are then extracted.

### MDL-Clust

The MDL-CLust method claims to perform clustering of subsequences. However, since clustering time series subsequences is generally ineffective, the authors propose disregarding data that does not fit into any cluster and avoiding overlapping subsequences. Thus, the output of MDL-CLust can be fully interpreted as motif sets. 
More specifically, the method utilizes the MDL principle to form clusters. In each iteration, we can either create a new cluster (by selecting the first two members using a classic PairMotif algorithm), add a subsequence to an existing cluster, or merge two clusters. We select the operation that most effectively reduces the description length. The algorithm terminates when no usable data remains or further reduction in the time series description length is no longer possible.

### LoCoMotif 

The LoCoMotif method addresses the challenge of variable length by searching for time-warped motifs at potentially different time scales within a time series. The process begins with the LoCo step, where the Self-Similarity Matrix of the time series is utilized to construct paths based on a principle similar to Dynamic Time Warping (DTW). The paths with the highest accumulated similarity in this matrix are identified. In the second step, these subpaths are grouped to create candidate Motifs. The method then assesses the encoding capacity of these candidates using a quality score that combines the similarity between occurrences with the overall coverage of the Motif set.

## Results 

A summary of the results can be found in the results/results_summary folder. The notebook read_results.ipynb can be used to read the results in order to obtain the various figures presented in the article, as well as some additional figures. 
Detailed results for each Research Question can be downloaded from the following links:

- RQ1: https://kiwi.cmla.ens-cachan.fr/index.php/s/ZNmpm8be5gQ4zSg
- RQ2: https://kiwi.cmla.ens-cachan.fr/index.php/s/48BPg5Xb2tFk2gr
- RQ3: https://kiwi.cmla.ens-cachan.fr/index.php/s/dpp8XGC46KLDrFz
- RQ4: https://kiwi.cmla.ens-cachan.fr/index.php/s/TYx2i5asFqwjkNq
- RQ5: https://kiwi.cmla.ens-cachan.fr/index.php/s/dYdpca3bpTqm8mi
- RQ6: https://kiwi.cmla.ens-cachan.fr/index.php/s/DSK879jg68ipf5z

