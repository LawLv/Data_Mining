import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from shingling import Shingling
from minhashing import MinHashing
from lsh import LSH
from compare_signatures import CompareSignatures
from compare_sets import CompareSets


import re
import random


# load dataset
data_path = '../dataset/True.csv'
df = pd.read_csv(data_path)
all_documents = df['title'].values

n = 1000
generator = np.random.default_rng(seed=42)
documents = generator.choice(all_documents, n)

# Generate Shingles
sh = Shingling(k=5)
shingling_tokens = list(map(lambda document: sh.generate_shingles(document), documents))

similarities = []
for i in range(n - 1):
    token_1 = shingling_tokens[i]
    for j in range(i + 1, n):
        token_2 = shingling_tokens[j]
        similarities.append(CompareSets.jaccard_similarity(token_1, token_2))

sns.histplot(x=similarities, bins=100)
plt.xlabel("Similarity")
plt.ylabel("Number of Pairs")
plt.title("Distribution of Document Similarities")
plt.savefig("similarity_distribution.png")
plt.show()


# para
SHINGLING_SIZE = 5
NUM_HASHES = 100
threshold = 0.1

# Sample
sh = Shingling(SHINGLING_SIZE)
generator = np.random.default_rng(seed=42)
documents = generator.choice(all_documents, 1000)
band_sizes = [5, 10, 20, 30, 40, 50]

n_pairs = []
approx_n_pairs = []

for b in band_sizes:
    # init MinHash and LSH instance
    minhash = MinHashing(NUM_HASHES)
    lsh = LSH(bands=b, rows=NUM_HASHES // b)

    # generate sig dic
    signatures = {}
    for i, doc in enumerate(documents):
        shingles = sh.generate_shingles(doc)
        hashed_shingles = sh.hash_shingles(shingles)
        signature = minhash.generate_signature(hashed_shingles)
        signatures[i] = signature

    # 使用 LSH 找到近似相似对
    approx_similar_items = lsh.find_similar_pairs(signatures, threshold)
    approx_n_pairs.append(len(approx_similar_items))

    # 使用精确 Jaccard 相似度计算相似对的数量
    true_similar_items = set()
    for i in range(len(documents)):
        for j in range(i + 1, len(documents)):
            shingles_i = sh.generate_shingles(documents[i])
            shingles_j = sh.generate_shingles(documents[j])
            similarity = CompareSets.jaccard_similarity(shingles_i, shingles_j)
            if similarity >= threshold:
                true_similar_items.add((i, j))
    n_pairs.append(len(true_similar_items))

# 绘制结果
plt.plot(band_sizes, n_pairs, label='True Similar Items')
plt.plot(band_sizes, approx_n_pairs, label='Approximate Similar Items (LSH)')
plt.ylabel('Number of similar pairs')
plt.xlabel('Band size')
plt.legend()
plt.title("Effect of Band Size on Similar Pairs Count")
plt.savefig("Different_band_size.png")

