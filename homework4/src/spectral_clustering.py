import networkx as nx
import numpy as np
from scipy import linalg
from sklearn.cluster import KMeans
from typing import Callable, Dict, Tuple

auto_select = {
    'auto': lambda eigenlist, k: np.argmin(np.ediff1d(eigenlist)) + 1
}


def spectral_clustering(G: nx.Graph,) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes k clusters in the graph with spectral clustering
    每个节点所属的簇标签、Fiedler 向量，以及图的邻接矩阵
    Returns:
    a numpy array of shape (number of vertices,) containing the label for each vertex,
    a numpy array of shape (number of vertices,) containing the Fiedler vector,
    a numpy matrix of shape (number of vertices, number of vertices) containing the adjacency matrix
    """

    print('Clustering now ... ...')

    A = nx.to_numpy_array(G)  # Adjacency matrix
    D = np.diagflat(np.sum(A, axis=1))  # Degree matrix
    D_inv = np.linalg.inv(np.sqrt(D))  # Inverse
    L = D_inv @ A @ D_inv  # Normalized Laplacian Matrix
    values, vectors = linalg.eigh(L)   # Eigenvalues and Vectors ranked ascending
    
    # k = auto_select['auto'](values, None)  # find Eigengap 较小的特征值提供了连通性信息
    k = 4
    print('The estimated optimal number of clusters is {}.'.format(k))

    X = vectors[:, -k:]  # n×k, k个最大的特征值对应的特征向量, 每行表示一个节点在 k 维空间中的表示
    Y = X / np.linalg.norm(X, axis=1, keepdims=True)  # Normalization
    result = KMeans(n_clusters=k).fit(Y).labels_  # k-维空间中的点分为 𝑘 个簇

    print('Finished.')

    return result, vectors[:, 1], A

