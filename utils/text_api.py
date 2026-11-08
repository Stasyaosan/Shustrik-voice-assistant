import requests


def text_post(text, side):
    url = "http://127.0.0.1:5000/api/speak"

    # Тестовые данные в формате JSON
    payload = {"text": text, "side": side}

    try:
        response = requests.post(url, json=payload)
        print("Статус-код ответа:", response.status_code)
        print("Ответ сервера:", response.json())
    except requests.exceptions.ConnectionError:
        print(
            "Ошибка: Не удалось подключиться. Убедитесь, что Flask-сервер запущен!"
        )
