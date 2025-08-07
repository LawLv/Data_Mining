import hashlib

from compare_signatures import CompareSignatures

class LSH:
    def __init__(self, bands, rows):
        self.bands = bands # bands count
        self.rows = rows # rows of each bands

    # hash the band, return value
    def hash_band(self, band):
        return hashlib.sha1("".join(map(str, band)).encode()).hexdigest()

    def find_similar_pairs(self, signatures, threshold):
        # (self, sig dic, 相似性阈值)
        candidates = {} # A dic，store doc id with same hash value. <band_hash, [doc_id1, doc_id2, ...]>
        for doc_id, signature in signatures.items():
            for band_index in range(self.bands):
                band = signature[band_index * self.rows: (band_index + 1) * self.rows] # set a band with length of 'rows'
                band_hash = self.hash_band(band) # hash a band
                if band_hash not in candidates:
                    candidates[band_hash] = []
                candidates[band_hash].append(doc_id)

        similar_pairs = set()
        for docs in candidates.values():
            if len(docs) > 1: # doc num > 1
                for i in range(len(docs)): # compute each pairs' similarity
                    for j in range(i + 1, len(docs)):
                        if CompareSignatures.signature_similarity(signatures[docs[i]], signatures[docs[j]]) >= threshold:
                            similar_pairs.add((docs[i], docs[j]))
        return similar_pairs
