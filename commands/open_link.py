import webbrowser
from sentence_transformers import util
from googletrans import Translator
from utils.models import model_sentence_transformers
from urls.config import URLS
import json



class LinkSearcher:
    def __init__(self):
        self.translator = Translator()
        self.model = model_sentence_transformers

        links = {}

        with open(URLS['user_links'], 'r', encoding="utf-8") as f:
            data = json.load(f)
            for i in data:
                links[i['name']] = i['link']

        self.link_names = list(links.keys())
        self.link_urls = list(links.values())
        self.links_embs = self.model.encode(self.link_names, convert_to_tensor=True)

    def search_l(self, query):
        translated_query = self.translator.translate(query, dest='en').text
        query_em = self.model.encode(translated_query, convert_to_tensor=True)

        similarities = util.cos_sim(query_em, self.links_embs)[0]

        results = []
        for idx, similarity in enumerate(similarities):
            if similarity.item() >= 0.5:  # Для ссылок порог можно немного снизить
                results.append({
                    'index': idx,
                    'similarity': similarity.item(),
                    'name': self.link_names[idx],
                    'url': self.link_urls[idx]
                })

        results.sort(key=lambda x: x['similarity'], reverse=True)

        if results:
            print(f"\nНайдено {len(results)} совпадений для ссылок:")
            for r in results[:3]:
                print(f"  - {r['name']} (сходство: {r['similarity']:.3f})")

            return self.open_link(results[0])
        else:
            print('Ссылка не найдена')
            return 'Ссылка не найдена'

    def open_link(self, link):
        try:
            if isinstance(link['url'], list):
                for i in link['url']:
                    webbrowser.open(i)
            else:
                webbrowser.open(link['url'])

            try:
                if any(ord(char) > 127 for char in link['name']):
                    display_name = link['name']
                else:
                    translated = self.translator.translate(link['name'], dest='ru')
                    display_name = translated.text
            except:
                display_name = link['name']

            print(f'Открыто в браузере: {display_name} (сходство: {link["similarity"]:.3f})')
            return f'Открыто: {display_name}'

        except Exception as e:
            error_msg = f'Ошибка при открытии ссылки {link["name"]}: {e}'
            print(error_msg)
            return error_msg


