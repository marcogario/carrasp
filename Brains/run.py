import time
from multiprocessing import Queue, Manager, Process

from wheels import SteeringDirection, Wheels
from teledoc.camera import Camera
from teledoc.launcher import Launcher, LauncherCmd


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
        self.teledoc_camera = None
        self.teledoc_launcher = None
        self.pdict = {}

    def start_processes(self):
        # Kill switch for processes
        self.ns.do_quit = False
        self.start_wheels()
        self.start_senses()
        self.start_teledoc_launcher()
        self.start_teledoc_camera()
        #self.start_demo()

    def _start_process(self, name, instance):
        p = Process(target=instance.control_loop)
        p.start()
        self.pdict[name] = p
            
    def start_demo(self):
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

    def start_wheels(self):
        """Start the Wheels Process"""
        self.ns.target_steering = SteeringDirection.NONE
        self.ns.target_throttle = 0
        # Create class and process
        self.wheels = Wheels(self.ns)
        self.wheels.setup()
        self._start_process("wheels", self.wheels)
        print("Wheels started.")

    def start_teledoc_camera(self):
        """Start Teledoc Camera Process"""
        self.ns.frame = None
        self.ns.camera_freq = (1.0 / 3.0)
        # Create class and process
        self.teledoc_camera = Camera(self.ns)
        self.teledoc_camera.setup()
        self._start_process("teledoc-camera", self.teledoc_camera)
        print("Senses started.")

    def start_teledoc_launcher(self):
        """Start the Teledoc Launcher Process"""
        cmd_q = Queue()
        self.teledoc_launcher = Launcher(self.ns)
        self.teledoc_launcher.setup(cmd_q)
        self._start_process("teledoc-launcher", self.teledoc_launcher)
        print("Teledoc started.")

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
