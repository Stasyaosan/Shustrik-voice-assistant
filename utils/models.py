from sentence_transformers import SentenceTransformer
from urls.config import URLS

model_sentence_transformers = SentenceTransformer(URLS['transformers_model'])
