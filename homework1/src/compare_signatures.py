class CompareSignatures:
    @staticmethod
    def signature_similarity(sig1, sig2):
        match_count = sum(1 for i in range(len(sig1)) if sig1[i] == sig2[i])
        return match_count / len(sig1)