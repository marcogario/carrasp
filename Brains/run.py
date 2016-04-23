import time
from multiprocessing import Queue, Manager, Process

from wheels import SteeringDirection, Wheels
from camera import Camera
from launcher import Launcher, LauncherCmd
from web import WebInterface


class Brains(object):
    """Coordinate all running processes."""

    def __init__(self):
        # Processes are started within this Manager.
        # This allow the processes to share information
        # Through the underlying Namespace
        self.mgr = Manager()
        self.ns = self.mgr.Namespace()

        self.wheels = None
        self.senses = None
        self.front_camera = None
        self.back_camera = None
        self.launcher = None
        self.web_ui = None
        self.pdict = {}

    def start_processes(self):
        # Kill-switch for processes
        self.ns.do_quit = False
        self.start_wheels()
        self.start_senses()
        self.start_launcher()
        self.start_cameras()
        self.start_web()

    def _start_process(self, instance_name):
        instance = getattr(self, instance_name)
        p = Process(target=instance.control_loop)
        p.start()
        self.pdict[instance_name] = p
        print("'%s' started." % instance_name)

    def start_demo(self):
        """Shows how to use the namespace to share data among processes."""
        self.ns.msg = "0"
        from demo import Demo
        d = Demo(self.ns)
        d.setup()
        p = Process(name='demo',
                    target=d.control_loop)
        p.start()
        for i in range(3):
            time.sleep(1)
            self.ns.msg = str(i)
            print("Updating msg to %d" %i)

    def start_senses(self):
        """Start Senses Process"""
        pass

    def start_web(self):
        """Starts the Web-Interface"""
        self.web_ui = WebInterface(self.ns,
                                   self.launcher.cmd_q)
        self._start_process("web_ui")

    def start_wheels(self):
        """Start the Wheels Process"""
        self.ns.target_steering = SteeringDirection.NONE
        self.ns.target_throttle = 0
        # Create class and process
        self.wheels = Wheels(self.ns)
        self._start_process("wheels")

    def start_cameras(self):
        """Start Cameras Processes"""
        self.ns.camera_freq = (1.0 / 3.0)
        self.ns.front_camera_frame = None
        self.ns.back_camera_frame = None
        # Create class and process
        self.front_camera = Camera(self.ns, is_front=True)
        self._start_process("front_camera")
        self.back_camera = Camera(self.ns, is_front=False)
        self._start_process("back_camera")

    def start_launcher(self):
        """Start the Teledoc Launcher Process"""
        cmd_q = Queue()
        self.launcher = Launcher(self.ns, cmd_q=cmd_q)
        self._start_process("launcher")

    def shutdown(self):
        print("Exiting...")
        self.ns.do_quit = True
        time.sleep(1)
        for p in self.pdict:
            if self.pdict[p].is_alive():
                self.pdict[p].terminate()

def main():
    b = Brains()
    b.start_processes()
    raw_input("Press Enter to exit...")
    b.shutdown()

if __name__ == '__main__':
    main()
