from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import base64
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iboror_chat_secret'
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=10_000_000)

users = {}  # sid -> username
messages = []  # son 50 mesajı sakla

@socketio.on('connect')
def on_connect():
    pass

@socketio.on('join')
def on_join(data):
    username = data.get('username', 'Anonim')
    users[request.sid] = username
    messages_to_send = messages[-50:]
    emit('history', messages_to_send)
    msg = {'type': 'system', 'text': f'{username} katıldı'}
    messages.append(msg)
    emit('message', msg, broadcast=True)
    emit('user_list', list(users.values()), broadcast=True)

@socketio.on('disconnect')
def on_disconnect():
    username = users.pop(request.sid, 'Biri')
    msg = {'type': 'system', 'text': f'{username} ayrıldı'}
    messages.append(msg)
    emit('message', msg, broadcast=True)
    emit('user_list', list(users.values()), broadcast=True)

@socketio.on('send_message')
def on_message(data):
    username = users.get(request.sid, 'Anonim')
    msg = {'type': 'text', 'username': username, 'text': data.get('text', '')}
    messages.append(msg)
    if len(messages) > 200:
        messages.pop(0)
    emit('message', msg, broadcast=True)

@socketio.on('send_image')
def on_image(data):
    username = users.get(request.sid, 'Anonim')
    msg = {'type': 'image', 'username': username, 'image': data.get('image', '')}
    messages.append(msg)
    if len(messages) > 200:
        messages.pop(0)
    emit('message', msg, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
