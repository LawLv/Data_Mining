import hashlib

class Shingling:
    def __init__(self, k):
        self.k = k # length

    def generate_shingles(self, document):
        shingles = set()
        for i in range(len(document) - self.k + 1):
            shingles.add(document[i:i + self.k])
        return shingles

    def hash_shingles(self, shingles):
        return {hashlib.sha1(shingle.encode()).hexdigest()[:8] for shingle in shingles}
