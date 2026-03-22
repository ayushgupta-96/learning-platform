# backend/run.py
import eventlet
eventlet.monkey_patch()
from backend.app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)