import wikipedia
import re


class Wiki:
    def __init__(self):
        # Устанавливаем русский язык
        wikipedia.set_lang('ru')
        # Обязательно задаём User-Agent — иначе Wikimedia возвращает
        # не-JSON ответ и библиотека падает с JSONDecodeError
        wikipedia.set_user_agent(
            'MyWikiBot/1.0 (https://example.com; my-email@example.com)'
        )

    def search(self, query):
        if not query:
            return None

        try:
            # Ищем подходящий заголовок страницы (query может быть фразой)
            titles = wikipedia.search(query)
            if not titles:
                return {'error': 'Страница не найдена'}

            page = wikipedia.page(titles[0], auto_suggest=False)

            # Возвращаем первые 5 предложений
            return {
                'title': page.title,
                'url': page.url,
                'content': ' '.join(self.split_reg(page.content)[:5])
            }
        except wikipedia.exceptions.DisambiguationError as e:
            return {
                'error': f'Неоднозначность! Возможные варианты: {e.options[:5]}'
            }
        except wikipedia.exceptions.PageError:
            return {'error': 'Страница не найдена'}
        except wikipedia.exceptions.RedirectError:
            return {'error': 'Слишком много перенаправлений'}
        except Exception as e:
            return {'error': f'Произошла ошибка: {type(e).__name__}: {e}'}

    def split_reg(self, text):
        return re.split(r'(?<=[.!?])\s+(?=[A-ZА-ЯЁ])', text)