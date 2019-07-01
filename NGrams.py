from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from scipy.sparse import hstack
from sklearn.preprocessing import OneHotEncoder
from sklearn import mixture
from sklearn.metrics import mutual_info_score,adjusted_rand_score,adjusted_mutual_info_score
from nltk.cluster import KMeansClusterer
import nltk
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import AgglomerativeClustering
import loadXES


def ngrams_BPI_2015(logName, vectorsize):
    filename="input/"+logName+".csv"
    data = pd.read_csv(filename,sep=',',encoding='latin-1',na_values=['null'],keep_default_na=False)
    cluster = data['cluster'].values
    
#     #attributi lista nominali 
#     LAN = ['action_code_seq','activityNameEN_seq','concept_name_seq','question_seq','monitoringResource_seq','org_resource_seq']
#     #attributi nominali
#     AN = ['case_caseStatus','case_Responsible_actor','case_last_phase','case_requestComplete','case_parts','case_termName']
#     #attributi lista numerici
# #         LAV = ['delta','delta_p','delta_df','case_SUMleges_seq']
#     #attributi numerici
#     AV = ['duration','duration_df','duration_p']

    #attributi lista nominali 
    LAN = ['case_termName_seq', 'case_parts_seq','case_requestComplete_seq','case_last_phase_seq','case_Responsible_actor_seq','case_caseStatus_seq','action_code_seq','activityNameEN_seq','concept_name_seq','question_seq','monitoringResource_seq','org_resource_seq']
    #attributi nominali
    AN = []
    #attributi lista numerici
    LAV = ['delta','delta_p','delta_df','case_SUMleges_seq']
    #attributi numerici
    AV = ['duration','duration_df','duration_p']
    
    data = computeMatrix(data, LAN, AN, LAV, AV)
    svd = TruncatedSVD(n_components=vectorsize, random_state=42)
    data = svd.fit_transform(data)
    y=[el-1 for el in cluster]
    return data, y
    #clustering(data, cluster, 5)


def computeMatrix(data, lan, an, lav, av):
    toReturn = []
    
    for x in lan:
        vec = CountVectorizer(ngram_range = (1,3),
                              analyzer = "word",  
                              tokenizer = None,  
                              preprocessor = None, 
                              stop_words = None,  
                              token_pattern = r"(?u)\b\w+\b")
        
        toReturn.append(vec.fit_transform(data[x]))
           
    for x in av:
        toReturn.append(data[x].values.reshape(data.shape[0],1))

    for x in lav:
        vec = CountVectorizer(ngram_range = (1,3),
                              analyzer = "word",  
                              tokenizer = None,  
                              preprocessor = None, 
                              stop_words = None,  
                              token_pattern = r"(?u)\b\w+\b")
        
        toReturn.append(vec.fit_transform(data[x]))

    for x in an:
        enc = OneHotEncoder(handle_unknown='ignore')
        toReturn.append(enc.fit_transform(data[x].values.reshape(data.shape[0],1)))
      

    toReturn = hstack(toReturn)
    
    return toReturn


def clustering(data, cluster, n_classes):
    print('\n------------------GMM\n')
    assigned_clusters = mixture.GaussianMixture(n_components=n_classes,covariance_type='tied').fit_predict(data)
 
    print ('Mutual_info_score =',mutual_info_score(cluster-1,assigned_clusters))
    print ('Adjusted_mutual_info_score =',adjusted_mutual_info_score(cluster-1,assigned_clusters,average_method='min'))
    print ('Adjusted_rand_scor =',adjusted_rand_score(cluster-1,assigned_clusters))

        
    
    
    print('\nK_MEANS')
     
    kclusterer = KMeansClusterer(num_means=n_classes, distance=nltk.cluster.util.cosine_distance)
    assigned_clusters = kclusterer.cluster(data, assign_clusters=True)
         
    print ('Mutual_info_score =',mutual_info_score(cluster-1,assigned_clusters))
    print ('Adjusted_mutual_info_score =',adjusted_mutual_info_score(cluster-1,assigned_clusters,average_method='min'))
    print ('Adjusted_rand_scor =',adjusted_rand_score(cluster-1,assigned_clusters))

def endCluster(folderName, assigned_clusters, vectorsize, clusterType, corpus):
    trace_list = loadXES.get_trace_names(folderName+".xes")
    clusterResult= {}
    for doc_id in range(len(corpus)):
        clusterResult[trace_list[doc_id]]=assigned_clusters[doc_id]


    resultFile= open('output/'+folderName+'NGVS'+str(vectorsize)+clusterType+'.csv','w')
    for doc_id in range(len(corpus)):
        resultFile.write(trace_list[doc_id]+','+str(assigned_clusters[doc_id])+"\n")

    resultFile.close()
    print("done with " , clusterType , " on event log ", folderName)