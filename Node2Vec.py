import argparse
import numpy as np
import networkx as nx 
import node2vec
from gensim.models import Word2Vec
import gensim

def parse_args():
    '''
    Parses the node2vec arguments.
    '''
    parser = argparse.ArgumentParser(description="Run node2vec.")

    parser.add_argument('--input', nargs='?', default='graph/karate.edgelist',
                        help='Input graph path')

    parser.add_argument('--output', nargs='?', default='karate.emb',
                        help='Embeddings path')

    parser.add_argument('--dimensions', type=int, default=16,
                        help='Number of dimensions. Default is 128.')

    parser.add_argument('--walk-length', type=int, default=80,
                        help='Length of walk per source. Default is 80.')

    parser.add_argument('--num-walks', type=int, default=10,
                        help='Number of walks per source. Default is 10.')

    parser.add_argument('--window-size', type=int, default=10,
                        help='Context size for optimization. Default is 10.')

    parser.add_argument('--iter', default=1, type=int,
                      help='Number of epochs in SGD')

    parser.add_argument('--workers', type=int, default=8,
                        help='Number of parallel workers. Default is 8.')

    parser.add_argument('--p', type=float, default=1,
                        help='Return hyperparameter. Default is 1.')

    parser.add_argument('--q', type=float, default=1,
                        help='Inout hyperparameter. Default is 1.')

    parser.add_argument('--weighted', dest='weighted', action='store_true',
                        help='Boolean specifying (un)weighted. Default is unweighted.')
    parser.add_argument('--unweighted', dest='unweighted', action='store_false')
    parser.set_defaults(weighted=False)

    parser.add_argument('--directed', dest='directed', action='store_true',
                        help='Graph is (un)directed. Default is undirected.')
    parser.add_argument('--undirected', dest='undirected', action='store_false')
    parser.set_defaults(directed=False)

    return parser.parse_args()

def read_graph(args):
    '''
    Reads the input network in networkx.
    '''
    if args.weighted:
        G = nx.read_edgelist(args.input, nodetype=str, data=(('weight',float),), create_using=nx.DiGraph())
    else:
        G = nx.read_edgelist(args.input, nodetype=str, create_using=nx.DiGraph(), encoding='latin-1')
        for edge in G.edges():
            G[edge[0]][edge[1]]['weight'] = 1

    return G

def learn_embeddings(args, folderName, vectorsize, walks):
    '''
    Learn embeddings by optimizing the Skipgram objective using SGD.
    '''
    walks2 = []
    walks = [map(str,walk) for walk in walks]   
    
    for w in walks:
        walks2.append(list(w))
    model = Word2Vec(walks2, size=args.dimensions, window=args.window_size, min_count=0, sg=1, workers=args.workers, iter=args.iter)
    model.save('output/'+folderName+'N2VVS'+str(vectorsize) +'.model')
    model.wv.save_word2vec_format(args.output)
    return

def startCluster(folderName, vectorsize):
    model= gensim.models.Doc2Vec.load('output/'+folderName+'N2VVS'+str(vectorsize) +'.model')

    corpus=getTrace(folderName)
    vectors = []
    print("inferring vectors")
    for line in corpus:
        inferred_vector = model.wv[line]
        vectors.append(inferred_vector)
    print("done")
    return vectors, corpus

def endCluster(folderName, assigned_clusters, vectorsize, clusterType, corpus):
    trace_list = getTrace(folderName)
    clusterResult= {}
    for doc_id in range(len(corpus)):
        clusterResult[trace_list[doc_id]]=assigned_clusters[doc_id]


    resultFile= open('output/'+folderName+'N2VVS'+str(vectorsize)+clusterType+'.csv','w')
    for doc_id in range(len(corpus)):
        resultFile.write(trace_list[doc_id]+','+str(assigned_clusters[doc_id])+"\n")

    resultFile.close()
    print("done with " , clusterType , " on event log ", folderName)

def getTrace(folderName):
    text_file = open("input/"+folderName+".graph.real", "r")
    y=[]
    for line in text_file.readlines():
        y.append(line.split(",")[0])
    return y

def getY(folderName):
    text_file = open("input/"+folderName+".graph.real", "r")
    y=[]
    for line in text_file.readlines():
        y.append(int(line.split(",")[1]))
    return y

def extract(logName, vectorsize):
    f=open("output/"+logName+"N2VVS"+str(vectorsize)+".node2vec", "r")
    f1=open("output/"+logName+"N2VVS"+str(vectorsize)+"_trace.node2vec", "w")
    dic={}
    for line in f:
        if("trace_" in line):
            id=line[6:]
            id=id[:id.index(" ")]
            dic[id]=line
    c=0
    while(len(dic)>0):
        if(str(c) in dic):
            f1.write(dic[str(c)])
        del dic[str(c)]
        c+=1
    f1.close()
    f.close()