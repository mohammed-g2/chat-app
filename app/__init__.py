import secrets
from flask import Flask, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, leave_room, join_room
from flask_cors import CORS
from config import options


cors = CORS()
db = SQLAlchemy()
socket = SocketIO()

def create_app(config_name: str) -> Flask:
    """Create and configure the application"""
    app = Flask(__name__)
    app.config.from_object(options[config_name])

    cors.init_app(app)
    db.init_app(app)
    socket.init_app(app)

    rooms = []

    def generate_room(rooms: list=rooms):
        room_id = None
        while not room_id:
            token = secrets.token_urlsafe(4)
            if token not in rooms:
                rooms.append(token)
                room_id = token
        return room_id
    
    # --- Socket routes ----

    @socket.on('connect')
    def connect():
        room_id = session.get('room_id')
        if not room_id or room_id not in rooms:
            return
        join_room(room_id)
        print('Client connected, room:', room_id)
        emit('response', {'data': 'client joined room'}, to=room_id)

    @socket.on('disconnect')
    def disconnect():
        room_id = session.get('room_id')
        if not room_id or room_id not in rooms:
            return
        leave_room(room_id)
        print('Client disconnected, room:', room_id)
        emit('response', {'data': 'client leaved room'}, to=room_id)
    
    @socket.on('message')
    def message(msg):
        room_id = session.get('room_id')
        if not room_id or room_id not in rooms:
            return
        emit('response', {'data': msg['data']}, to=room_id)
    
    # --- App Routes ---

    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/rooms')
    def list_rooms():
        return render_template('rooms.html', rooms=rooms)
    
    @app.route('/new-room', methods=['POST'])
    def new_room():
        room_id = generate_room()
        session['room_id'] = room_id
        return redirect(url_for('chat'))

    @app.route('/join/<room_id>')
    def join_room_by_id(room_id):
        if not room_id in rooms:
            return redirect(url_for('list_rooms'))
        session['room_id'] = room_id
        return redirect(url_for('chat'))
    
    @app.route('/chat')
    def chat():
        room_id = session.get('room_id')
        if room_id not in rooms:
            return redirect(url_for('list_rooms'))
        return render_template('chat.html', room_id=room_id)
    
    return app
