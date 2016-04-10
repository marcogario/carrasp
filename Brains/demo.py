import time

class Demo(object):
    def __init__(self, namespace):
        self.ns = namespace

    def setup(self):
        print("Setup")

    def control_loop(self):
        print("Demo: control_loop has started")
        while self.ns.do_quit is False:
            print(self.ns.msg)
            time.sleep(1)
        self.shutdown()
        print("Demo: control_loop has stopped")

    def shutdown(self):
        print("Shutdown")
