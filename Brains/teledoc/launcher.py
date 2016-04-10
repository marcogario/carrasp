import time
import Queue


class LauncherCmd(object):
    Up, Down, Left, Right, Fire = range(5)


class Launcher(object):
    def __init__(self, namespace):
        self.ns = namespace
        self.launcher = None

    def setup(self, cmd_q):
        self.launcher = LauncherMock()
        self.cmd_q = cmd_q

    def control_loop(self):
        print("Teledoc: Launcher control_loop has started")
        while not self.ns.do_quit:
            try:
                cmd = self.cmd_q.get(block=True,
                                                 timeout=0.5)
                # Process command
                self.update_with_command(cmd)
            except Queue.Empty:
                pass
        print("Teledoc: Launcher control_loop has stopped")

    def update_with_command(self, cmd):
        if cmd == LauncherCmd.Up:
            self.launcher.step_up()
        elif cmd == LauncherCmd.Down:
            self.launcher.step_down()
        elif cmd == LauncherCmd.Left:
            self.launcher.step_left()
        elif cmd == LauncherCmd.Right:
            self.launcher.step_right()
        else:
            assert cmd == LauncherCmd.Fire, \
                "Unknown cmd value %d" % cmd
            self.launcher.fire()


class LauncherMock(object):

    def fire(self):
        print("Pew! Pew!")

    def step_up(self):
        print("Up!")

    def step_down(self):
        print("Down!")

    def step_left(self):
        print("Left!")

    def step_right(self):
        print("Right!")



class LauncherController(object):

    def __init__(self):
        import usb.core
        self.dev = usb.core.find(idVendor=0x2123, idProduct=0x1010)
        if self.dev is None:
            raise ValueError('Launcher not connected!')

        if self.dev.is_kernel_driver_active(0) is True:
            self.dev.detach_kernel_driver(0)

        self.dev.set_configuration()

    def up(self):
        self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x02,0x00,0x00,0x00,0x00,0x00,0x00])

    def down(self):
        self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x01,0x00,0x00,0x00,0x00,0x00,0x00])

    def left(self):
        self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x04,0x00,0x00,0x00,0x00,0x00,0x00])

    def right(self):
        self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x08,0x00,0x00,0x00,0x00,0x00,0x00])

    def stop(self):
        self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x20,0x00,0x00,0x00,0x00,0x00,0x00])

    def fire(self):
        self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x10,0x00,0x00,0x00,0x00,0x00,0x00])

    def step_up(self):
        self.up()
        time.sleep(0.05)
        self.stop()

    def step_down(self):
        self.down()
        time.sleep(0.05)
        self.stop()

    def step_left(self):
        self.left()
        time.sleep(0.05)
        self.stop()

    def step_right(self):
        self.right()
        time.sleep(0.05)
        self.stop()

if __name__ == "__main__":
    print("Demoing Launcher")
    lc = LauncherController()
    for f in [lc.step_up, lc.step_down, lc.step_left, lc.step_right]:
        for i in xrange(10):
            f()
            time.sleep(0.5)
    lc.fire()
