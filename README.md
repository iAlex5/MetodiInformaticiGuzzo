# Comparator for the analysis of embedding
The following work is born for the analysis of several embedding emerged in the last years, in particular the elaborate compares 3 different approaches: trace2vec, node2vec, nGram2vec. Clustered product outputs through the most common clustering techniques, such as:
    • K-Means;
    • Gaussian Mixture Model;
    • Support Vector Machine;
    • Hierarchical Clustering with Ward's method;
    • Random Forest;
    • Decision Tree;
    • Logistic Regression.
To provide reliable data the results are compared with accuracy measurements:
    • Precision
    • Recall
    • Rand Index
    • Normalized Mutual Information
    • F-Score

Except for nGram, the implementations of node2Vec and trace2vec refer to the following gitHub directories:

@inproceedings{node2vec-kdd2016,
author = {Grover, Aditya and Leskovec, Jure},
 title = {node2vec: Scalable Feature Learning for Networks},
 booktitle = {Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining},
 year = {2016}
}

Implementations of act2vec, trace2vec, log2vec, and model2vec are available alongside the data and models used for the experimental evaluation and full color figures on http://processmining.be/replearn. The implementations are based on the Gensim-library for unsupervised semantic modelling from plain text.

# How to Run?
You only need to:
-put your log in xes extension in the input folder
-put the log name in the variable logName in main.py
-set the number of cluster in the log in the variable NUM_CLUSTER
-execute main.py.
The method createInput from PrepareInput.py creates the other necessary files to execute.
The program assume that the folder output and toBePlotted already exist.

# dependencies / libraries:
* Python3
* gensim
* texttable
* nltk
* sklearn
* numpy
* matplotlib
* pandas
* scipy
* networkx
* argparse


