from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import BooleanProperty

from plyer import accelerometer, battery, compass, gps

from random import randint
import socket


UPDATE_FREQ = 1.0/10 # 10Hz
#RASP_ADDR = "192.168.42.42"
RASP_ADDR = "192.168.1.8"
RASP_PORT = 8080


class StatusPage(Widget):
    accelerometer_enabled = BooleanProperty(False)
    compass_enabled = BooleanProperty(False)
    gps_enabled = BooleanProperty(False)
    gps_data = {"status": "N/A"}
    rasp_conn = None
    rasp_conn_retry = 0

    def send_data(self, data):
        if self.rasp_conn is not None:
            self.rasp_conn.send(data)

    def try_connect(self, dt=None):
        msg = "Connecting to %s:%d" % (str(RASP_ADDR), RASP_PORT)
        self.ids.connection_status.text = msg
        print(msg)
        self.rasp_conn_retry += 1

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((RASP_ADDR, RASP_PORT))
            s.send("Hello World\n")
        except:
            self.ids.connection_status.text = "Failed (%d attempts)" % self.rasp_conn_retry
            if self.rasp_conn_retry < 10:
                # Retry in a bit
                Clock.schedule_once(self.try_connect, self.rasp_conn_retry)
            else:
                # Giving up
                self.ids.connect_btn.state = 'normal'
            return

        self.ids.connection_status.text = "Established"
        #data = s.recv(BUFFER_SIZE)
        self.rasp_conn = s


    def connect(self, args):
        _, do_connect = args
        do_connect = do_connect == 'down'

        if do_connect:
            self.try_connect()
        else:
            msg = "Disconnecting from %s:%d" % (str(RASP_ADDR), RASP_PORT)
            self.ids.connection_status.text = msg
            print(msg)
            if self.rasp_conn is not None:
                self.rasp_conn.close()
            self.ids.connection_status.text = "Disconnected"

    def update_accelerometer(self):
        value = None
        try:
            value = accelerometer.acceleration[:3]
        except:
            value = [randint(-10,10), randint(-10,10), randint(-10,10)]

        # Update GUI
        accelerometer_label = self.ids.accelerometer_value
        accelerometer_label.text = str(value)

        # Send Data
        self.send_data("%s : %s\n" % ("accelerometer", str(value)))

    def update_compass(self):
        value = None
        try:
            value = compass.orientation
        except:
            value = [randint(-10,10), randint(-10,10), randint(-10,10)]

        # Update GUI
        compass_label = self.ids.compass_value
        compass_label.text = str(value)

        # Send Data
        self.send_data("%s : %s\n" % ("compass", str(value)))

    def update_battery(self):
        value = None
        try:
            value = battery.status
        except:
            value = randint(-10,10)

        # Update GUI
        battery_status = self.ids.battery_status
        battery_status.text = "HTC Battery: %s" % str(value)

        # Note: Shall we send this to the server?

    def update_gps(self):
        value = self.gps_data

        # Update GUI
        gps_label = self.ids.gps_value
        gps_label.text = "GPS: %s" % str(value)

        self.send_data("%s : %s\n" % ("gps", value))

    def on_gps_location(self, **kwargs):
        self.gps_data['location'] = str(kwargs)

    def on_gps_status(self, stype, status):
        self.gps_data['status'] = "%s %s" % (stype, status)


    def update(self, dt):
        if self.accelerometer_enabled:
            self.update_accelerometer()
        if self.compass_enabled:
            self.update_compass()
        if self.gps_enabled:
            self.update_gps()
        self.update_battery()
        return

    def change_gps_status(self, args):
        _, is_active = args
        self.gps_enabled = is_active
        if is_active:
            print("Starting GPS")
            try:
                self.gps = gps
                self.gps.configure(on_location=self.on_gps_location,
                                   on_status=self.on_gps_status)
                self.gps.start()
            except NotImplementedError:
                print("GPS is not Available!!!")
        else:
            print("Stopping GPS")
            try:
                self.gps.stop()
            except:
                pass



class DesireApp(App):
    """This Apps sends sensor data to the Raspberry.

    The app itself runs in foreground, and provides status information.
    """

    gps = None
    gps_data = {'location':None, 'status':None}

    def build(self):
        status_page = StatusPage()
        # Startup the "cheap" sensors
        try:
            accelerometer.enable()
            compass.enable()
        except:
            pass


        Clock.schedule_interval(status_page.update, UPDATE_FREQ)
        #vibrator.vibrate(0.2)  # vibrate for 0.2 seconds
        return status_page

    def on_stop(self):
        pass

    def callback(self, instance, value):
        print('the switch', instance, 'is', value)


if __name__ == '__main__':
    DesireApp().run()
