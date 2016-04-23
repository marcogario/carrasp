from __future__ import unicode_literals

import time
import logging
import base64

from flask import Flask, render_template, request, Response
from flask.ext.socketio import SocketIO, emit

from launcher import LauncherCmd
from wheels import SteeringDirection


class WebInterface(object):

    def __init__(self, ns,
                 launcher_cmd_q=None):
        self.ns = ns
        self.launcher_cmd_q = launcher_cmd_q
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, logger=True)

        # Logging info
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        self.app.logger.addHandler(stream_handler)

        self.app.add_url_rule("/", "index", self.index)
        self.app.add_url_rule("/command", "command", self.command, methods=["POST"])
        # Debugging screen
        self.app.add_url_rule("/debug/camera", "camera", self.camera)
        self.app.add_url_rule("/debug/wheels", "wheels", self.wheels)

        # Note: This is nested within __init__ on purpose
        @self.socketio.on('front_camera')
        def front_camera(sid):
            frame = self.ns.front_camera_frame
            frame64 = base64.b64encode(frame)
            data = {
                'id': 0,
                'raw': 'data:image/jpeg;base64,' + frame64,
                'timestamp': time.time()
            }
            emit('front_frame', data)

        @self.socketio.on('back_camera')
        def back_camera(sid):
            frame = self.ns.back_camera_frame
            frame64 = base64.b64encode(frame)
            data = {
                'id': 0,
                'raw': 'data:image/jpeg;base64,' + frame64,
                'timestamp': time.time()
            }
            emit('back_frame', data)

        @self.socketio.on('wheels')
        def wheels(sid):
            data = {
                'target_steering': self.ns.target_steering,
                'target_throttle': self.ns.target_throttle,
            }
            emit('wheels_data', data)


    def command(self):
        """command route."""
        command_id = request.form["command_id"]
        target = request.form["target"]
        if target == "launcher":
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
        elif target == "wheels":
            if command_id == "+":
                self.ns.target_throttle = (self.ns.target_throttle + 10) % 100
            elif command_id == "-":
                self.ns.target_throttle = (self.ns.target_throttle - 10) % 100
            elif command_id == "left":
                if self.ns.target_steering == SteeringDirection.RIGHT:
                    self.ns.target_steering = SteeringDirection.NONE
                else:
                    self.ns.target_steering = SteeringDirection.LEFT
            elif command_id == "right":
                if self.ns.target_steering == SteeringDirection.LEFT:
                    self.ns.target_steering = SteeringDirection.NONE
                else:
                    self.ns.target_steering = SteeringDirection.RIGHT


        return "done"

    def control_loop(self):
        self.socketio.run(self.app, host='0.0.0.0', port=5000)

    def index(self):
        """Video streaming home page."""
        return render_template('index.html')

    def camera(self):
        if request.args.get("id") == "0":
            is_front = True
        else:
            is_front = False

        if is_front:
            frame = self.ns.front_camera_frame
        else:
            frame = self.ns.back_camera_frame
        return Response(frame, mimetype="image/jpeg")

    def wheels(self):
        target_steering = self.ns.target_steering
        target_throttle = self.ns.target_throttle
        data = (target_steering, target_throttle)
        return Response("<html><h2>Target Steering: %d</h2>" \
                        "<h2>Target Throttle: %d</h2>"\
                        "</html>" % data)



if __name__ == '__main__':
    class MockNamespace(object):
        front_camera_frame = open("static/nosignal.jpg").read()
    ns = MockNamespace()
    web_ui = WebInterface(ns)
    web_ui.control_loop()


#    socketio.run(app, host='0.0.0.0', port=5000)
                 # policy_server=False,
                 # transports='websocket, xhr-polling, xhr-multipart')
