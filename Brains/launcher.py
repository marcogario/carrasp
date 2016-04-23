import time
import Queue


class LauncherCmd(object):
    Up, Down, Left, Right, Fire = range(5)


class Launcher(object):
    def __init__(self, namespace, cmd_q):
        self.ns = namespace
        self.launcher = None
        self.cmd_q = cmd_q
        try:
            self.launcher = LauncherController()
        except:
            self.launcher = LauncherMock()

    def control_loop(self):
        print("Teledoc: Launcher control_loop has started")
        self.launcher.reset_pos()
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

    def reset_pos(self, target=0):
        print("Resetting...")

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
        self.step = 0.2
        self.position = 0
        self.max_position = 21

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
        time.sleep(self.step)
        self.stop()

    def step_down(self):
        self.down()
        time.sleep(self.step)
        self.stop()

    def step_left(self):
        self.left()
        time.sleep(self.step)
        self.stop()

    def step_right(self):
        self.right()
        time.sleep(self.step)
        self.stop()

    def reset_pos(self, target=11):
        print("Launcher: Initializing...")
        self.down()
        time.sleep(2)
        self.stop()
        self.step_up()

        self.right()
        time.sleep(6)
        self.stop()
        self.position = 0
        print("Launcher: Going to middle")
        self.goto(target)

    def goto(self, target):
        if target < 0 :
            target = 0
        elif target > self.max_position:
            target = self.max_position

        if self.position < target:
            while self.position != target:
                self.step_left()
                time.sleep(0.5)
                self.position += 1
        else:
            while self.position != target:
                self.step_right()
                time.sleep(0.5)
                self.position -= 1

if __name__ == "__main__":
    print("Demoing Launcher")
    lc = LauncherController()

    lc.reset_pos()
    time.sleep(1)
    lc.goto(0)
    time.sleep(1)
    lc.goto(11)
    time.sleep(1)
    lc.goto(21)
    time.sleep(1)
    lc.reset_pos()
