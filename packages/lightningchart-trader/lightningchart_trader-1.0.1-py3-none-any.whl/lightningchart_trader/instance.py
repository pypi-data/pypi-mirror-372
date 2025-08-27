from __future__ import annotations
import os
import sys
import time
import threading
import socket
import queue
import uuid
import msgpack
import requests
import webbrowser
from IPython import get_ipython
from IPython.display import IFrame, display
from flask import Flask, request, render_template, send_from_directory, Response
from flask_socketio import SocketIO, join_room

LOCALHOST = 'localhost'
host_name = '0.0.0.0'
base_dir = '.'
if hasattr(sys, '_MEIPASS'):
    base_dir = os.path.join(sys._MEIPASS)


def get_free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((LOCALHOST, 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class Instance:
    def __init__(self, license_key: str):
        self.id = str(uuid.uuid4()).split('-')[0]
        self.license_key = license_key
        self.items = list()
        self.storage = dict()
        self.pending_get_results = dict()
        self.connected_clients = dict()
        self.preserve_data = True
        self.server_is_open = False
        self.server_port = None

        # Initialize Flask and SocketIO
        self.session = requests.Session()
        retry_adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.session.mount('http://', retry_adapter)
        self.app = Flask(
            __name__,
            static_folder=os.path.join(base_dir, 'static'),
            template_folder=os.path.join(base_dir, 'static'),
        )
        self.app.config['SECRET_KEY'] = 'secret!'
        self.socketio = SocketIO(self.app, async_mode='gevent', ping_timeout=60)

        # HTTP routes
        self.app.route('/', methods=['GET'])(self._http_index)
        self.app.route('/send', methods=['POST'])(self._http_send)
        self.app.route('/get', methods=['POST'])(self._http_get)
        self.app.route('/storage', methods=['GET'])(self._http_storage)
        self.app.route('/static/<path:path>', methods=['GET'])(self._http_static)

        # SocketIO events
        self.socketio.on_event('connect', self._sio_connect)
        self.socketio.on_event('disconnect', self._sio_disconnect)
        self.socketio.on_event('join', self._sio_join)
        self.socketio.on_event('get_result', self._sio_get_result)

    # ----- Public methods -----

    def send(self, id: str, command: str, arguments: dict = None):
        data = {'id': str(id), 'command': command, 'args': arguments or {}}
        if not self.server_is_open:
            self.items.append(data)
        else:
            binary_data = msgpack.packb(data)
            try:
                response = self.session.post(
                    f'http://{LOCALHOST}:{self.server_port}/send?room={self.id}',
                    data=binary_data,
                    headers={'Content-Type': 'application/msgpack'},
                )
                if response.ok:
                    return True
            except requests.RequestException as e:
                print(e)

    def get(self, id: str, command: str = None, arguments: dict = None):
        get_id = str(uuid.uuid4()).split('-')[0]
        data = {
            'get_id': get_id,
            'id': str(id),
            'command': command,
            'args': arguments or {},
        }
        if not self.server_is_open:
            try:
                if get_ipython().__class__.__name__ == 'ZMQInteractiveShell':
                    self.open_in_notebook()
                    for _ in range(20):
                        if self._room_response():
                            break
                        time.sleep(0.5)
                else:
                    self.open_in_browser()
            except Exception as e:
                raise Exception(f'Chart was not opened, and it failed to open automatically. Please open it manually.Error: {e}')
        elif not self._room_response():
            for _ in range(20):
                if self._room_response():
                    break
                time.sleep(0.5)

        binary_data = msgpack.packb(data)
        try:
            response = self.session.post(
                f'http://{LOCALHOST}:{self.server_port}/get?room={self.id}&get_id={get_id}',
                data=binary_data,
                headers={'Content-Type': 'application/msgpack'},
            )
            if response.ok:
                data = msgpack.unpackb(response.content, raw=False)
                return data
            elif response.status_code == 400:
                raise Exception('Chart is not open, cannot execute command. Call open() method first.')
            elif response.status_code == 500:
                raise Exception('Unexpected error occurred, cannot execute command.')
        except requests.RequestException as e:
            print(e)

    def open(
        self,
        method: str = None,
        live: bool = False,
        width: int | str = '100%',
        height: int | str = 600,
    ):
        if method not in ('browser', 'notebook', 'link'):
            try:
                method = 'notebook' if get_ipython().__class__.__name__ == 'ZMQInteractiveShell' else 'browser'
            except NameError:
                method = 'browser'
        if (live or method == 'link') and not self.server_is_open:
            self._start_server()
            for item in self.items:
                self.send(item['id'], item['command'], item['args'])

        if method == 'notebook':
            return self.open_in_notebook(width=width, height=height)
        elif method == 'link':
            return f'http://{LOCALHOST}:{self.server_port}/?id={self.id}'
        else:
            return self.open_in_browser()
        
    def open_in_browser(self):
        if not self.server_is_open:
            self._start_server()
            for i in self.items:
                self.send(i['id'], i['command'], i['args'])
        try:
            webbrowser.open(f'http://{LOCALHOST}:{self.server_port}/?id={self.id}')
            for _ in range(20):
                if self._room_response():
                    return True
                time.sleep(0.5)
        except requests.exceptions.ConnectionError as e:
            print(e)
        return False

    def open_in_notebook(self, width: int | str = '100%', height: int | str = 600):
        if not self.server_is_open:
            self._start_server()
            for i in self.items:
                self.send(i['id'], i['command'], i['args'])
        try:
            return display(
                IFrame(
                    src=f'http://{LOCALHOST}:{self.server_port}/?id={self.id}',
                    width=width,
                    height=height,
                )
            )
        except requests.exceptions.ConnectionError as e:
            print(e)

    def close(self):
        if self.server_is_open:
            for client in self.connected_clients.keys():
                self.socketio.emit('shutdown', to=client)
            self.socketio.stop()
            self.server_is_open = False

    # ----- Private methods -----

    def _start_server(self):
        try:
            self.server_port = get_free_port()
            server_thread = threading.Thread(
                target=lambda: self.socketio.run(
                    self.app,
                    host=host_name,
                    port=self.server_port,
                    debug=True,
                    log_output=False,
                    use_reloader=False,
                )
            )
            server_thread.start()
            self.server_is_open = True
        except Exception as e:
            raise Exception(f'Failed to start server on port {self.server_port}. {e}')

    def _room_response(self):
        return self.id in self.connected_clients.values()

    def _wait_for_get_result(self, get_id, timeout=5, poll_interval=0.5, max_polls=10):
        q = queue.Queue()
        self.pending_get_results[get_id] = q
        for _ in range(max_polls):
            if not q.empty():
                break
            self.socketio.sleep(poll_interval)
        try:
            result = q.get(timeout=timeout)
        except queue.Empty:
            result = None
        finally:
            del self.pending_get_results[get_id]
        return result

    # ----- HTTP Routes -----

    def _http_index(self):
        room = request.args.get('id')
        return render_template('index.html', room=room, license_key=self.license_key)

    def _http_static(self, path):
        return send_from_directory('./static', path)

    def _http_send(self):
        room = request.args.get('room')
        binary_data = request.data

        if room not in self.storage:
            self.storage[room] = []

        save = False
        if room in self.connected_clients.values():
            self.socketio.emit('item', binary_data, to=room)
        else:
            save = True

        if self.preserve_data or save:
            data = msgpack.unpackb(binary_data)
            self.storage[room].append(data)

        return '', 200

    def _http_get(self):
        room = request.args.get('room')
        get_id = request.args.get('get_id')
        binary_data = request.data

        if room not in self.connected_clients.values():
            return Response('', status=400)

        self.socketio.emit('get_request', binary_data, to=room)
        result = self._wait_for_get_result(get_id)

        if result is None:
            return Response('', status=500)
        return Response(msgpack.packb(result), mimetype='application/msgpack')

    def _http_storage(self):
        room = request.args.get('room')
        try:
            data = msgpack.packb(self.storage[room])
            if not self.preserve_data:
                del self.storage[room]
            return Response(data, mimetype='application/msgpack')
        except KeyError:
            return Response('Room not found', status=404)

    # ----- SocketIO Events -----

    def _sio_connect(self):
        self.connected_clients[request.sid] = 'default'

    def _sio_disconnect(self):
        del self.connected_clients[request.sid]

    def _sio_join(self, room):
        join_room(room)
        self.connected_clients[request.sid] = room
        if room in self.storage:
            self.socketio.emit('exec', to=room)

    def _sio_get_result(self, binary_data):
        data = msgpack.unpackb(binary_data)
        get_id = data['get_id']
        result = data['result']
        if get_id in self.pending_get_results:
            self.pending_get_results[get_id].put(result)
