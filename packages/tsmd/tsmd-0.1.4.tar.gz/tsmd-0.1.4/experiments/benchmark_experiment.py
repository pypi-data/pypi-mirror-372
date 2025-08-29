from tsmd.competitors.latentmotifs import LatentMotif
import numpy as np 
import pandas as pd
import time
import os
from tsmd.tools.metric import SampleScore,EventScore, AdjustedMutualInfoScore
from joblib import Parallel, delayed
from tsmd.tools.utils import transform_label_to_mask,get_params_by_ts
import inspect
from data.Synthetic.synthetic_signal import SignalGenerator
import json

class Experiment: 

    def __init__(self,algorithms:list, thresholds = np.linspace(0,1,101),njobs=1,verbose = True) -> None:
   


        """Initialization

        Args:
            algorithms (list): list of algorithm classes
            
            thresholds (np.ndarray, optional): numpy array of thresholds to consider for the event based metric. Defaults to numpy.linspace(0,1,101).
        """
        self.algorithms = algorithms

        self.thresholds = thresholds
        self.njobs = njobs
        self.verbose = verbose



    def compute_scores(self,label,prediction): 

        single_pred = np.clip(np.sum(prediction,axis=0),0,1).reshape(1,-1) 
        single_label = np.clip(np.sum(label,axis=0),0,1).reshape(1,-1)

        scores = []

        #single sample score
        p,r,f = SampleScore().score(single_label,single_pred)
        scores.append(["sss-precision",p])
        scores.append(["sss-recall",r])
        scores.append(["sss-fscore",f])

        #sample score 
        p,r,f = SampleScore().score(label,prediction)
        scores.append(["ss-precision",p])
        scores.append(["ss-recall",r])
        scores.append(["ss-fscore",f])

        # weigthed sample score 
        p,r,f = SampleScore(averaging="weighted").score(label,prediction)
        scores.append(["w-ss-precision",p])
        scores.append(["w-ss-recall",r])
        scores.append(["w-ss-fscore",f])

        #single event score
        lp,lr,lf = EventScore().score(single_label,single_pred,self.thresholds)
        for t,p,r,f in zip(self.thresholds,lp,lr,lf): 
            scores.append([f"ses-precision_{np.round(t,2)}",p])
            scores.append([f"ses-recall_{np.round(t,2)}",r])
            scores.append([f"ses-fscore_{np.round(t,2)}",f])
        scores.append(["ses-auc-precision",np.mean(lp)])
        scores.append(["ses-auc-recall",np.mean(lr)])
        scores.append(["ses-auc-fscore",np.mean(lf)])

        #event score
        lp,lr,lf = EventScore().score(label,prediction,self.thresholds)
        for t,p,r,f in zip(self.thresholds,lp,lr,lf): 
            scores.append([f"es-precision_{np.round(t,2)}",p])
            scores.append([f"es-recall_{np.round(t,2)}",r])
            scores.append([f"es-fscore_{np.round(t,2)}",f])
        scores.append(["es-auc-precision",np.mean(lp)])
        scores.append(["es-auc-recall",np.mean(lr)])
        scores.append(["es-auc-fscore",np.mean(lf)])

        # weighted event score
        lp,lr,lf = EventScore(averaging="weighted").score(label,prediction,self.thresholds)
        for t,p,r,f in zip(self.thresholds,lp,lr,lf): 
            scores.append([f"w-es-precision_{np.round(t,2)}",p])
            scores.append([f"w-es-recall_{np.round(t,2)}",r])
            scores.append([f"w-es-fscore_{np.round(t,2)}",f])
        scores.append(["w-es-auc-precision",np.mean(lp)])
        scores.append(["w-es-auc-recall",np.mean(lr)])
        scores.append(["w-es-auc-fscore",np.mean(lf)])

        #ajusted mutual information
        scores.append(["amis",AdjustedMutualInfoScore().score(label,prediction)])

        return scores
    
    def signal_algo_class_experiment(self,signal_name,signal,label,algo_class,config): 
        "Return a DF"
        #keep only labels row that are activated by the signal 
        label = label[label.sum(axis=1)>0]

        #update the number of patterns to predict if required
        params_to_keep=inspect.getfullargspec(algo_class.__init__)[0]
        t_config={key : config[key] for key in params_to_keep if key in config.keys() }
        try:
            n_repetitions=1

            if algo_class==LatentMotif:
                #non deterministic algo, for each timeseries we do 5 iterations
                n_repetitions=5
            #get predictions

            for rep in range(n_repetitions):
                try:
                    algo = algo_class(**t_config)
                    start = time.time()
                    algo.fit(signal)
                    end = time.time()

                    algo_name= algo_class.__name__
                    exec_time = end-start
                    #compute scores
                    
                    scores = self.compute_scores(label,algo.prediction_mask_)
                    tdf = pd.DataFrame(scores,columns=["metric","score"])

    
                    n_patterns = label.shape[0]
                    predicted_n_patterns = algo.prediction_mask_.shape[0]

                    if n_repetitions > 1:   
                        signal_id=signal_name +'_iteration_' + str(rep+1) 
                    else:
                        signal_id=signal_name
                    self.save_results(self.dataset_path,tdf,algo_name,exec_time,signal_id,n_patterns,predicted_n_patterns,t_config)
                except:
                    pass
                if n_repetitions > 1:   
                        signal_id=signal_name +'_iteration_' + str(rep+1) 
                else:
                    signal_id=signal_name
                #we register the execution time even if the methods failed to fit
                results_path=self.results_path
                if not os.path.exists(results_path):
                    os.makedirs(results_path)
                infos_path = results_path + 'Infos/' + algo_name + '/'
                if not os.path.exists(infos_path):
                    os.makedirs(infos_path)

                file_name=algo_name + '_' + signal_id

                run_infos={'signal_name':signal_id ,'algo_name':algo_name,
                'execution_time': exec_time}
                if not os.path.exists(infos_path+file_name+'.json'):
                    with open(infos_path+file_name+'.json', 'w') as f:
                        json.dump(run_infos, f) 

            tdf["algorithm"] = algo_class.__name__
            tdf["execution_time"] = end - start
            tdf["signal_name"] = signal_name
            tdf["n_patterns"] = label.shape[0]
            tdf["predicted_n_patterns"] = algo.prediction_mask_.shape[0]
            
            if self.verbose: 
                s1 = np.round(tdf[tdf["metric"] == "es-auc-fscore"].score.values[0],2)
                s2 = np.round(tdf[tdf["metric"] == "amis"].score.values[0],2)
                print(f"signal_name: {signal_name}, algo: {algo_class.__name__}, , f-auc: {s1}, ami: {s2}")

            return tdf 

        except: 
            s= f"signal_name: {signal_name}, algo: {algo_class.__name__} failed to fit."
            if self.verbose: 
                print(s)
            if self.logs_path_ is not None:
                with open(self.logs_path_,"a") as f: 
                    f.write(s +"\n")

         
    def get_dataset_from_path(self,dataset_path):

        self.dataset_path=dataset_path

        data_path= dataset_path + 'Data/'
        metadata_path= dataset_path + 'MetaData/'

        dataset=[]
        labels=[]
        names=[]
        configs=[]


        for f in sorted(os.listdir(data_path)):
                
                df=pd.read_csv(data_path+f,skiprows=1).to_numpy()
                dataset.append(df[:,1].astype(float))
                lab=df[:,2].astype(str)
                lab[lab=='-1.0']='-1'
                labels.append(transform_label_to_mask(lab))

                json_f=f.split('csv')[0]+'json'
                K,R_min,R_max,R_mean,w_mean,w_median,w_std,w_min,w_max,k,k_max=get_params_by_ts(metadata_path+json_f)
                config={}

                config['n_patterns']=K
                config['radius']=R_mean
                config['wlen']=w_mean
                config['wlen_for_persistence']=max(0,w_mean-w_std)
                config['min_wlen']=w_min
                config['max_wlen']=w_max
                config['k']=k 
                config['k_max']=int(k_max)

                config['distance_name']= 'UnitEuclidean'
                configs.append(config)

                names.append(f.split('.csv')[0])
        
        return dataset,labels,names,configs
    
    def get_synthetic_dataset(self,dataset_path,generator_params,n_ts=100):
        

        self.dataset_path=dataset_path
        ts_gen=SignalGenerator(**generator_params)
        config={}
        config['n_patterns']=generator_params['n_motifs']
        #to change:
        config['radius']=np.mean(3*generator_params['motif_length']*generator_params['noise_amplitude'])
        config['wlen']=int(np.mean(generator_params['motif_length']))
        config['wlen_for_persistence']=int(np.min(generator_params['motif_length']*(1-generator_params['length_fluctuation'])))
        config['min_wlen']=int(np.min(generator_params['motif_length']*(1-generator_params['length_fluctuation'])))
        config['max_wlen']=int(np.max(generator_params['motif_length']*(1+generator_params['length_fluctuation'])))
        if 'exact_occurences' in generator_params.keys():
            config['k']=generator_params['exact_occurences']
            config['k_max']=int(max(generator_params['exact_occurences']))
        else:
            config['k']=(generator_params['min_rep']+generator_params['max_rep'])/2
            config['k_max']=int(generator_params['max_rep'])

        config['distance_name']= 'UnitEuclidean'
        configs=[config]*n_ts
        dataset=[]
        labels=[]
        names=[]
        for i in range(n_ts):
            name='repetition_'+str(i)
            data,lab=ts_gen.generate()
            dataset.append(data)
            labels.append(lab)
            names.append(name)

        return dataset,labels,names,configs


    def save_results(self,dataset_path,df,algo_name,exec_time,signal_name,n_patterns,predicted_n_patterns,config):
    
        results_path= self.results_path
        if not os.path.exists(results_path):
            os.makedirs(results_path)
        metrics_path= results_path +'Metrics/' + algo_name + '/'
        infos_path = results_path + 'Infos/' + algo_name + '/'
        if not os.path.exists(metrics_path):
            os.makedirs(metrics_path)
        if not os.path.exists(infos_path):
            os.makedirs(infos_path)

        file_name=algo_name + '_' + signal_name

        run_infos={'signal_name':signal_name ,'algo_name':algo_name,
        'execution_time': exec_time, 'n_patterns':n_patterns, 
        'predicted_patterns': predicted_n_patterns,'config':config}

        with open(infos_path+file_name+'.json', 'w') as f:
            json.dump(run_infos, f)

        df.to_csv(metrics_path+file_name+'.csv')
        

    def run_experiment(self,dataset_path,generator_params=None,results_path=None,backup_path = None,batch_size=10,logs_path = None,verbose = True,n_ts=100)->np.ndarray:
        """_summary_

        Args:
            dataset (np.ndarray): array of signals, signal shape (L,), variable length allowed
            labels (np.ndarray): array of labels, label shape (L,), variable length allowed
            signal_configs (pd.DataFrame, optional): Dataframe containing the configuration of the synthetic generator for each signals.
            backup_path (str, optional): Path to store df in case of big experiment. If None no saving. Defaults to None.
            batch_size (int, optional)
            verbose (bool, optional): verbose. Defaults to True.

        Returns:
            pd.DataFrame: scores_df
        """
        self.logs_path_ = logs_path
        if results_path is None:
            self.results_path= self.dataset_path + 'Results/'
        else:
            self.results_path = results_path


        if generator_params is None:
            self.dataset,self.labels,self.names,self.configs= self.get_dataset_from_path(dataset_path)
        else:
            self.dataset,self.labels,self.names,self.configs= self.get_synthetic_dataset(dataset_path,generator_params,n_ts=n_ts)


        n_signals = len(self.dataset)
        
        if backup_path != None: 
            n_batches  = n_signals//batch_size
            if n_batches >0:
                batches =[zip(self.dataset[i*batch_size:(i+1)*batch_size],self.labels[i*batch_size:(i+1)*batch_size],self.names[i*batch_size:(i+1)*batch_size],self.configs[i*batch_size:(i+1)*batch_size]) for i in range(n_batches)]
            else: 
                batches = []
            if n_signals % batch_size !=0: 
                batches.append(zip(self.dataset[n_batches*batch_size:],self.labels[n_batches*batch_size:],self.names[n_batches*batch_size:],self.configs[n_batches*batch_size:]))
        else:
            batches = [zip(self.dataset,self.labels,self.names,self.configs)]
        
        self.df_ = pd.DataFrame()

        counts = 0
        for batch in batches: 
            results = Parallel(n_jobs=self.njobs)(
                delayed(self.signal_algo_class_experiment)(signal_name,signal,label,algo,config) 
                for signal,label,signal_name,config in batch
                for id_a,algo in enumerate(self.algorithms))
            counts = min(counts+batch_size,n_signals)
            self.df_= pd.concat((self.df_,*results)).reset_index(drop = True)
            self.df_ = self.df_.astype({"metric":str, "score":float, "algorithm":str,"signal_name":str, "n_patterns":int, "predicted_n_patterns":int})

            if backup_path != None: 
                self.df_.to_csv(backup_path)

            if verbose:
                print(f"Achieved [{counts}/{n_signals}]")

        return self.df_  