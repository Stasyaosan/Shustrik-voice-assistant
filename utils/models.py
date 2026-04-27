from sentence_transformers import SentenceTransformer
from urls.config import URLS
from dotenv import load_dotenv
from os import getenv

load_dotenv()

if getenv('ONLINE_MODELS') == 'true':
    model_sentence_transformers = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
else:
    model_sentence_transformers = SentenceTransformer(URLS['transformers_model'])
