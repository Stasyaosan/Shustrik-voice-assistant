from sentence_transformers import SentenceTransformer
from urls.config import URLS
from dotenv import load_dotenv
from os import getenv
import os

load_dotenv()

model_path = str(URLS['transformers_model'])

if getenv('ONLINE_MODELS') == 'true':
    model_sentence_transformers = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
else:
    if not os.path.exists(model_path):
        print(f"Локальная модель не найдена. Скачиваю в {model_path}...")

        # Скачиваем из Hugging Face по имени модели
        model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        tmp_model = SentenceTransformer(model_name)

        # Создаем все родительские папки, если их нет, и сохраняем модель
        os.makedirs(model_path, exist_ok=True)
        tmp_model.save(model_path)
        print("Модель успешно скачана и сохранена локально!")
    model_sentence_transformers = SentenceTransformer(str(URLS['transformers_model']))
