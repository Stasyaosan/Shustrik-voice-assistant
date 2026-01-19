import wikipediaapi


class Wiki:
    def __init__(self):
        self.wiki = wikipediaapi.Wikipedia(
            language='ru',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='Shustrik (stasyaosan@inbox.ru)'
        )

    def search(self, query):
        search_results = self.wiki.page(query)
        if not search_results.exists():
            print('Не найдено')
            return []
        print(search_results.text)


s = Wiki()
s.search("норвежская_лесная_кошка")