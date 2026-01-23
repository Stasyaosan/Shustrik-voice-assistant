import wikipedia
import re


class Wiki:
    def __init__(self):
        wikipedia.set_lang('ru')

    def search(self, query):
        if query:
            page = wikipedia.page(query)
            return {
                'title': page.title,
                'content': ' '.join(self.split_reg(page.content)[:5])
            }

    def split_reg(self, text):
        return re.split(r'(?<=[.!?])\s+(?=[A-ZA-Я])', text)
