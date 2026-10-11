from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def index():
    return render_template('index.html')


# API Эндпоинт, куда ваш python-скрипт будет слать текст
@app.route('/api/speak', methods=['POST'])
def handle_speak():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "Missing text field"}), 400

    text = data['text']

    # Мгновенно отправляем текст всем подключенным веб-клиентам по WebSocket
    socketio.emit('api_message', {'text': text})

    return jsonify({"status": "sent"}), 200


if __name__ == '__main__':
    # ВАЖНО: Запускаем Flask через socketio, а не app.run()
    socketio.run(app, port=5000, debug=True)
