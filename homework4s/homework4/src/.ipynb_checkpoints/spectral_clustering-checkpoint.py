import networkx as nx
import numpy as np
from scipy import linalg
from sklearn.cluster import KMeans
from typing import Callable, Dict, Tuple

def spectral_clustering(
        G: nx.Graph, k
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes k clusters in the graph with spectral clustering
    Returns a numpy array of shape (number of vertices,) containing the label for each vertex,
                     a numpy array of shape (number of vertices,) containing the Fiedler vector,
                     a numpy matrix of shape (number of vertices, number of vertices) containing the adjacency matrix
    """

    print('Computing clusters...')

    A = nx.to_numpy_array(G) # 邻接矩阵
    D = np.diagflat(np.sum(A, axis=1)) # 度矩阵
    D_inv = np.linalg.inv(np.sqrt(D))
    L = D_inv @ A @ D_inv # 标准化拉普拉斯矩阵
    values, vectors = linalg.eigh(L)  # eigenvalues and vectors in ascending order
    # k = find_k(values, max_k = 10)
    print('The estimated optimal number of clusters is {}.'.format(k))

    X = vectors[:, -k:]
    Y = X / np.linalg.norm(X, axis=1, keepdims=True)
    result = KMeans(n_clusters=k).fit(Y).labels_

    print('Clusters computed.')

    return result, vectors[:, 1], A

