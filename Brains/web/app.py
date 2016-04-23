from __future__ import unicode_literals

import time
import logging
import base64

from flask import Flask, render_template, request
from flask.ext.socketio import SocketIO, emit

# TODO: Move things around so that this cna be imported
class LauncherCmd(object):
    Up, Down, Left, Right, Fire = range(5)


class WebInterface(object):

    def __init__(self, ns):
        self.ns = ns


    def setup(self, launcher_cmd_q):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app)
        self.launcher_cmd_q = launcher_cmd_q

        # Logging info
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        self.app.logger.addHandler(stream_handler)

        self.app.add_url_rule("/", "index", self.index)
        self.app.add_url_rule('/command', "command", self.command, methods=["POST"])

        @self.socketio.on('stream')
        def stream(foo):
            print("Stream")
            ns = self._brains_namespace
            frame = base64.b64encode(ns.frame())
            data = {
                'id': 0,
                'raw': 'data:image/jpeg;base64,' + frame,
                'timestamp': time.time()
            }
            emit('frame', data)

    def command(self):
        """command route."""
        command_id = request.form["command_id"]
        if command_id == "up":
            cmd = LauncherCmd.Up
        elif command_id == "down":
            cmd = LauncherCmd.Down
        elif command_id == "left":
            cmd = LauncherCmd.Left
        elif command_id == "right":
            cmd = LauncherCmd.Right
        elif command_id == "fire":
            cmd = LauncherCmd.Fire
        else:
            raise KeyError("Unknown command provided")
        self.launcher_cmd_q.put(cmd)
        return "done"

    def control_loop(self):
        self.socketio.run(self.app, host='0.0.0.0', port=5000)

    def index(self):
        """Video streaming home page."""
        return render_template('index.html')






if __name__ == '__main__':
    class MockNamespace(object):
        frame = None
    ns = MockNamespace()
    web_ui = WebInterface(ns)
    web_ui.setup(None)
    web_ui.control_loop()


#    socketio.run(app, host='0.0.0.0', port=5000)
                 # policy_server=False,
                 # transports='websocket, xhr-polling, xhr-multipart')
