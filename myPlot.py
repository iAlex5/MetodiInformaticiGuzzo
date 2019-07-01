import numpy as np
import matplotlib.pyplot as plt

logName='BPIC15GroundTruth'
clustering=["KMeans", "GMM", "SVM", "T2VH", "RandomForest", "DecisionTree", "LogisticRegression"]
colors=['tab:blue', 'tab:red', 'tab:green', 'tab:brown', 'tab:grey']
label=("Cluster 1", "Cluster 2", "Cluster 3", "Cluster 4", "Cluster 5")

def plot(emb):
    x, y = getXY(emb)
    fig, ax = plt.subplots(2, 4, figsize=(16, 12), dpi=80)
    fig.suptitle(emb, fontsize=16)
    plt.gcf().canvas.set_window_title(emb)

    for alg in range(len(clustering)):
        cluster=getCluster(clustering[alg], emb)
        xs, ys=separe(x, y, cluster)
        for i in range(5):
            ax[alg//4, alg%4].scatter(xs[i], ys[i], c=colors[i], label=colors[i], alpha=0.3, edgecolors='none')

        ax[alg//4, alg%4].legend(labels=label)
        ax[alg//4, alg%4].grid(True)
        ax[alg//4, alg%4].set_title(clustering[alg])

    real=getReal()
    xs, ys=separe(x, y, real)
    for i in range(5):
        ax[1, 3].scatter(xs[i], ys[i], c=colors[i], label=colors[i], alpha=0.3, edgecolors='none')
    ax[1, 3].legend(labels=label)
    ax[1, 3].grid(True)
    ax[1, 3].set_title("Real")

    #plt.show()
    plotThread(plt).start()

def separe(x, y, cluster):
    if not(len(x)==len(y)==len(cluster)):
        print("bad dimensions")
        return
    xs=[[], [], [], [], []]
    ys=[[], [], [], [], []]
    for i in range(len(x)):
        ind=cluster[i]
        xs[ind].append(x[i])
        ys[ind].append(y[i])
    return xs, ys

def getXY(emb):
    f1=open("toBePlotted/"+logName+"_"+emb+"_2.vectors", "r")
    x=[]
    y=[]
    for line in f1:
        l=line.split(" ")
        if len(l)>1:
            x.append(float(l[0]))
            y.append(float(l[1]))
    return np.array(x), np.array(y)

def getCluster(alg, emb):
    f1=open("toBePlotted/"+logName+"_"+emb+"_"+alg+"_2.clusters", "r")
    x=[]
    for line in f1:
        x.append(int(line))
    return np.array(x)

def getReal():
    f1=open("input/"+logName+".real", "r")
    x=[]
    for line in f1:
        x.append(int(line.split(",")[1]))
    return np.array(x)

from threading import Thread
class plotThread (Thread):
   def __init__(self, plt):
      Thread.__init__(self)
      self.plt = plt
   def run(self):
       self.plt.show()