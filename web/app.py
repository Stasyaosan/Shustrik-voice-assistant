import os
from flask import Flask, request, jsonify, render_template
from flask_sock import Sock
import json
from urls.config import URLS

app = Flask(__name__)
sock = Sock(app)

# Список для хранения активных WebSocket-соединений
clients = []
FILE_PATH = URLS['user_links']

def load_data():
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


def save_data(data):
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def broadcast(payload):
    for client in list(clients):
        try:
            client.send(payload)
        except Exception:
            if client in clients:
                clients.remove(client)

@app.route('/')
def index():
    return render_template('index.html')

# WebSocket эндпоинт для браузерая
@sock.route('/ws')
def ws_connect(ws):
    clients.append(ws)
    try:
        URLS['user_links'] = URLS['user_links']
        if os.path.exists(URLS['user_links']):
            with open(URLS['user_links'], 'r', encoding='utf-8') as f:
                json_string = f.read()
            ws.send(json_string)

        while True:
            # Ждем сообщений от клиента (если нужно),
            # либо просто удерживаем соединение открытым
            data = ws.receive()
    except Exception:
        pass
    finally:
        # Удаляем клиента при отключении
        clients.remove(ws)

# API Эндпоинт, куда ваш python-скрипт шлет текст
@app.route('/api/speak', methods=['POST'])
def handle_speak():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "Missing text field"}), 400

    text = data['text']
    payload = json.dumps([{'text': text, 'side': data['side'], 'mode': 'message'}])

    # Рассылаем текст всем подключенным нативным веб-сокетам
    for client in clients:
        try:
            client.send(payload)
        except Exception:
            # Убираем сломанные соединения, если они не очистились автоматически
            if client in clients:
                clients.remove(client)

    return jsonify({"status": "sent"}), 200

@app.route('/api/add_link', methods=['POST'])
def add_link():
    name = request.form.get('name', '').strip()
    link = request.form.get('link', '').strip()
    if not name or not link:
        return jsonify({"error": "пустое имя или ссылка"}), 400

    data = load_data()

    for item in data:
        if item.get('name') == name:
            if not isinstance(item.get('link'), list):
                item['link'] = [item['link']] if item.get('link') else []
            item['link'].append(link)
            break
    else:
        data.append({'name': name, 'link': [link], 'mode': 'link'})

    save_data(data)
    broadcast(json.dumps(data, ensure_ascii=False))
    return jsonify({"status": "ok"}), 200


@app.route('/api/remove_link', methods=['POST'])
def remove_link():
    index = request.form.get('index')
    data = load_data()
    try:
        data.pop(int(index))
        save_data(data)
        broadcast(json.dumps(data, ensure_ascii=False))
        return jsonify({"status": "ok"}), 200
    except Exception:
        return jsonify({"error": "неверный индекс"}), 404


@app.route('/api/remove_url', methods=['POST'])
def remove_url():
    index = request.form.get('index')
    print(index)
    url = request.form.get('url')
    data = load_data()
    try:
        idx = int(index)
        item = data[idx]
        urls = item.get('link', [])
        if not isinstance(urls, list):
            urls = [urls] if urls else []
        if url not in urls:
            return jsonify({"error": "ссылка не найдена"}), 404

        urls.remove(url)
        item['link'] = urls

        save_data(data)
        broadcast(json.dumps(data, ensure_ascii=False))
        return jsonify({"status": "ok"}), 200
    except Exception:
        return jsonify({"error": "неверный индекс"}), 404


if __name__ == '__main__':
    app.run(port=5000)
