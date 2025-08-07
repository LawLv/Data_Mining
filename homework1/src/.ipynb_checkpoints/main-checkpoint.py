from shingling import Shingling
from minhashing import MinHashing
from lsh import LSH
from compare_signatures import CompareSignatures

from sklearn.datasets import fetch_20newsgroups
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import random
import nltk
nltk.download('stopwords')
nltk.download('wordnet')

class DocumentSimilarityProcessor:
    def __init__(self, k=5, num_hashes=100, bands=20, rows=5, threshold=0.2):
        self.shingling = Shingling(k)
        self.minhashing = MinHashing(num_hashes)
        self.lsh = LSH(bands, rows)
        self.threshold = threshold

    def process_documents(self, documents):
        signatures = {}
        for i, doc in enumerate(documents):
            shingles = self.shingling.generate_shingles(doc)
            hashed_shingles = self.shingling.hash_shingles(shingles)
            signature = self.minhashing.generate_signature(hashed_shingles)
            signatures[i] = signature
        return signatures

    def find_similar_documents(self, documents):
        signatures = self.process_documents(documents)
        similar_pairs = self.lsh.find_similar_pairs(signatures, self.threshold)
        return similar_pairs

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = re.sub(r'<.*?>', ' ', text)             
    text = re.sub(r'[^A-Za-z\s]', '', text)        
    words = text.lower().split()                   
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return ' '.join(words)

def load_and_clean_documents(documents, sample_size=15):
    sample_documents = random.sample(documents, sample_size)
    cleaned_documents = [clean_text(doc) for doc in sample_documents]
    return cleaned_documents

# load dataset
categories = ['comp.graphics']
newsgroups = fetch_20newsgroups(subset='all', categories=categories)
documents = newsgroups.data

cleaned_sample_documents = load_and_clean_documents(documents)
document_processor = DocumentSimilarityProcessor(k=5, num_hashes=100, bands=10, rows=10, threshold=0.2)

similar_pairs = document_processor.find_similar_documents(cleaned_sample_documents)

print("Similar document pairs:", similar_pairs)
