import random

class MinHashing:
    def __init__(self, num_hashes):
        self.num_hashes = num_hashes # num of hash functions
        self.hash_functions = [self._create_hash_function() for _ in range(num_hashes)]

    def _create_hash_function(self):
        a, b = random.randint(1, 1000), random.randint(1, 1000)
        return lambda x: (a * int(x, 16) + b) % 2**32

    def generate_signature(self, hashed_shingles):
        signature = []
        for h in self.hash_functions:
            min_hash = min(h(shingle) for shingle in hashed_shingles) # find the min hash value
            signature.append(min_hash)
        return signature
