import gensim
import loadXES

def learn(folderName,vectorsize):
    documents = loadXES.get_doc_XES_tagged(folderName+'.xes')
    print ('Data Loading finished, ', str(len(documents)), ' traces found.')

# build the model
    model = gensim.models.Doc2Vec(documents, dm = 0, alpha=0.025, vector_size= vectorsize, window=3, min_alpha=0.025, min_count=0)
    print('model corpus total words', model.corpus_total_words)
    
# start training
    nrEpochs= 10
    for epoch in range(nrEpochs):
        if epoch % 2 == 0:
            print ('Now training epoch %s'%epoch)
        model.train(documents,total_examples=len(documents), epochs=nrEpochs)
        model.alpha -= 0.002  # decrease the learning rate
        model.min_alpha = model.alpha  # fix the learning rate, no decay


    model.save('output/'+folderName+'T2VVS'+str(vectorsize) +'.model')
    model.save_word2vec_format('output/'+folderName+ 'T2VVS'+str(vectorsize) + '.word2vec')

def startCluster(folderName, vectorsize):
    corpus = loadXES.get_doc_XES_tagged(folderName+'.xes')
    print ('Data Loading finished, ', str(len(corpus)), ' traces found.')
    model= gensim.models.Doc2Vec.load('output/'+folderName+'T2VVS'+str(vectorsize) +'.model')

    vectors = []
    print("inferring vectors")
    for doc_id in range(len(corpus)):
        inferred_vector = model.infer_vector(corpus[doc_id].words)
        vectors.append(inferred_vector)
    print("done")
    return vectors, corpus

def endCluster(folderName, assigned_clusters, vectorsize, clusterType, corpus):
    trace_list = loadXES.get_trace_names(folderName+".xes")
    clusterResult= {}
    for doc_id in range(len(corpus)):
        clusterResult[trace_list[doc_id]]=assigned_clusters[doc_id]


    resultFile= open('output/'+folderName+'T2VVS'+str(vectorsize)+clusterType+'.csv','w')
    for doc_id in range(len(corpus)):
        resultFile.write(trace_list[doc_id]+','+str(assigned_clusters[doc_id])+"\n")

    resultFile.close()
    print("done with " , clusterType , " on event log ", folderName)

def getY(folderName):
    text_file = open("input/"+folderName+".real", "r")
    y=[]
    for line in text_file.readlines():
        y.append(int(line.split(",")[1]))
    return y