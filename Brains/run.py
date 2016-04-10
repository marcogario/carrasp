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
        self.teledoc = None
        self.pdict = {}

    def start_processes(self):
        # Kill switch for processes
        self.ns.do_quit = False
        self.start_demo()
        self.start_wheels()
        self.start_senses()
        self.start_teledoc()

    def start_demo(self):
        self.ns.msg = "0"
        from demo import Demo
        d = Demo(self.ns)
        d.setup()
        pdemo = Process(name='demo',
                        target=d.control_loop)
        pdemo.start()
        self.pdict['demo'] = pdemo

        for i in range(3):
            time.sleep(1)
            self.ns.msg = str(i)
            print("Updating msg to %d" %i)

    def start_wheels(self):
        """Start the Wheels Process"""
        self.ns.target_steering = SteeringDirection.NONE
        self.ns.target_throttle = 0
        # Create class and process
        self.wheels = Wheels(self.ns)
        self.wheels.setup()
        p = Process(name='wheels',
                    target=self.wheels.control_loop)
        p.start()
        self.pdict['wheels'] = p
        print("Wheels started.")

    def start_senses(self):
        """Start the Senses Process"""
        self.ns.frame = None
        self.ns.camera_freq = (1.0 / 3.0)
        # Create class and process
        # TODO: This should connect to Desire,
        # but now we use the camera from teledoc
        self.senses = Camera(self.ns)
        self.senses.setup()
        p = Process(name='senses',
                    target=self.senses.control_loop)
        p.start()
        self.pdict[p.name] = p
        print("Senses started.")

    def start_teledoc(self):
        """Start the Teledoc Process"""
        cmd_q = Queue()
        self.teledoc = Launcher(self.ns)
        self.teledoc.setup(cmd_q)
        p = Process(name='teledoc',
                    target=self.teledoc.control_loop)
        p.start()
        self.pdict[p.name] = p
        # Demoing Teledoc
        for cmd in [LauncherCmd.Up, LauncherCmd.Up,
                    LauncherCmd.Down, LauncherCmd.Down]:
            self.teledoc.cmd_q.put(cmd)
            time.sleep(1)
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
