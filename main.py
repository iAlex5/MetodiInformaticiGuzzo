import Trace2Vec
import Node2Vec
import node2vec
import NGrams
import prepareInput
import myPlot
import texttable
from texttable import Texttable
import nltk
import sklearn
from sklearn.mixture.gaussian_mixture import GaussianMixture
from nltk.cluster.kmeans import KMeansClusterer
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import hierarchical
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
import sklearn.metrics
import warnings
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import cross_validate

clustering=["KMeans", "GMM", "SVM", "T2VH", "RandomForest", "DecisionTree", "LogisticRegression"]
measure=["Precision", "Recall", "NMI", "F1", "RI"]
logName='BPIC15GroundTruth'
embed={"Trace2Vec": "T2V", "Node2Vec": "N2V", "NGrams": "NG"}
vectorsize=16
NUM_CLUSTERS=5


def main():
    prepareInput.createInput(logName)

    scores=[]
    #----------start Trace2Vec
    Trace2Vec.learn(logName,vectorsize)
    y=Trace2Vec.getY(logName)
    vectors, corpus=Trace2Vec.startCluster(logName, vectorsize)
    printMatrix(vectors, "Trace2Vec", "vectors")
    for alg in clustering:
        assigned_clusters=cluster(alg, vectors, y)
        printVector(assigned_clusters, "Trace2Vec", "clusters", alg)
        Trace2Vec.endCluster(logName, assigned_clusters, vectorsize, alg, corpus)
    #----------end Trace2Vec

    #----------start Node2Vec
    args=Node2Vec.parse_args()
    args.input="input/"+logName+".graph"
    args.output="output/"+logName+"N2VVS"+str(vectorsize)+".node2vec"
    nx_G = Node2Vec.read_graph(args)
    G = node2vec.Graph(nx_G, True, args.p, args.q)
    G.preprocess_transition_probs()
    walks = G.simulate_walks(args.num_walks, args.walk_length)
    Node2Vec.learn_embeddings(args, logName, vectorsize, walks)
    Node2Vec.extract(logName, vectorsize)
    
    y=Node2Vec.getY(logName)
    vectors, corpus=Node2Vec.startCluster(logName, vectorsize)
    printMatrix(vectors, "Node2Vec", "vectors")
    for alg in clustering:
        assigned_clusters=cluster(alg, vectors, y)
        printVector(assigned_clusters, "Node2Vec", "clusters", alg)
        Node2Vec.endCluster(logName, assigned_clusters, vectorsize, alg, corpus)
    #----------end Node2Vec

    #----------start NGrams
    vectors, y=NGrams.ngrams_BPI_2015(logName, vectorsize)
    printMatrix(vectors, "NGrams", "vectors")
    for alg in clustering:
        assigned_clusters=cluster(alg, vectors, y)
        printVector(assigned_clusters, "NGrams", "clusters", alg)
        NGrams.endCluster(logName, assigned_clusters, vectorsize, alg, [0]*len(vectors))
    #----------end NGrams

    scores.append(get_scores("Trace2Vec"))
    scores.append(get_scores("Node2Vec"))
    scores.append(get_scores("NGrams"))

    for score in scores:
        print_scores(score)
    
    if vectorsize==2:
        for emb in embed:
            myPlot.plot(emb)

def compute_scores(y_true, y_pred):
    scores = {} 
    scores["Precision"] = sklearn.metrics.precision_score(y_true,y_pred,average='micro')
    scores["Recall"] = sklearn.metrics.recall_score(y_true,y_pred,average='micro')
    scores["NMI"] = sklearn.metrics.normalized_mutual_info_score(y_true,y_pred,average_method='min')
    scores["F1"] = sklearn.metrics.f1_score(y_true,y_pred,average='micro')
    scores["RI"] = sklearn.metrics.adjusted_rand_score(y_true,y_pred)
    return scores

def getDict(file):
    text_file = open(file, "r")
    vec={}
    for line in text_file.readlines():
        read=line.split(",")
        vec[read[0].strip()]=read[1].strip()
    return vec

def get_scores(embedding):
    if(embedding=="Node2Vec"):
        yD=getDict("input/"+logName+".graph.real")
    else:
        yD=getDict("input/"+logName+".real")

    table=[[embedding]+measure]

    for alg in clustering:
        y_predD=getDict("output/"+logName+embed[embedding]+"VS"+str(vectorsize)+alg+".csv")
        y=[]
        y_pred=[]
        for trace in yD:
            y.append(yD[trace])
            y_pred.append(y_predD[trace])
        score=compute_scores(y, y_pred)
        line=[alg]
        for meas in measure:
            line.append(score[meas])
        table.append(line)
    return table

def print_scores(scores):
    t = Texttable()
    t.add_rows(scores)
    print(t.draw())

def cross_validation(classifier,vectors,y):
    return cross_val_predict(classifier, vectors, y, cv=5)

def cluster(clusterType, vectors, y):
    if(clusterType=="KMeans"):
        kclusterer = KMeansClusterer(NUM_CLUSTERS, distance=nltk.cluster.util.cosine_distance, repeats=25)
        assigned_clusters = kclusterer.cluster(vectors, assign_clusters=True)
        
    elif(clusterType=="GMM"):
        GMM=GaussianMixture(n_components=NUM_CLUSTERS)
        assigned_clusters=GMM.fit_predict(vectors)

    elif(clusterType=="SVM"):
        classifier=SVC(kernel='rbf', gamma='auto', random_state=0)
        #cross-validation
        assigned_clusters = cross_validation(classifier,vectors, y)

    elif(clusterType=="T2VH"):
        ret=hierarchical.ward_tree(vectors, n_clusters=NUM_CLUSTERS)
        children=ret[0]
        n_leaves=ret[2]
        assigned_clusters=hierarchical._hc_cut(NUM_CLUSTERS, children, n_leaves)

    elif(clusterType=="RandomForest"):
        classifier=RandomForestClassifier()
        #cross-validation
        assigned_clusters = cross_validation(classifier,vectors, y)
        # classifier.fit(vectors, y)
        # assigned_clusters=classifier.predict(vectors)

    elif(clusterType=="DecisionTree"):
        classifier=DecisionTreeClassifier()
        #cross-validation
        assigned_clusters = cross_validation(classifier,vectors, y)
        # classifier.fit(vectors, y)
        # assigned_clusters=classifier.predict(vectors)

    elif(clusterType=="LogisticRegression"):
        classifier=sklearn.linear_model.LogisticRegression()
        #cross-validation
        assigned_clusters = cross_validation(classifier,vectors, y)
        # classifier.fit(vectors, y)
        # assigned_clusters=classifier.predict(vectors)

    else:
        print(clusterType, " is not a predefined cluster type.")
        return
    return assigned_clusters

def printMatrix(vector, emb, name):
    f=open("toBePlotted/"+logName+"_"+emb+"_"+str(vectorsize)+"."+name, "w")
    for v in vector:
        for el in v:
            f.write(str(el)+" ")
        f.write('\n')

def printVector(vector, emb, name, alg):
    f=open("toBePlotted/"+logName+"_"+emb+"_"+alg+"_"+str(vectorsize)+"."+name, "w")
    for v in vector:
        f.write(str(v)+'\n')

warnings.filterwarnings("ignore")
main()