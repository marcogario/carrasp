from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock, mainthread
from kivy.utils import platform

from plyer import vibrator, tts, notification
from plyer import accelerometer, battery, compass, gps
from kivy.uix.camera import Camera


class StatusPage(Widget):
    camera = None
    gps_data = None

    def update(self, dt):
        acc3 = accelerometer.acceleration[:3]
        battery_status = battery.status
        compass_value = compass.orientation
        print("Desire dT : %f" % dt)
        print("Desire Acc: %s" %  str(acc3)) # (x,y,z)
        print("Desire Battery: %s" % str(battery_status)) # (%, isCharging)
        print("Desire Compass: %s" % str(compass_value))
        print("Desire GPS: %s -- %s" % (str(self.gps_data['location']),
                                        str(self.gps_data['status'])))
        print("Desire Camera: %s" % str(self.camera.texture))


class SensorsApp(App):
    service = None
    gps = None
    gps_data = {'location':None, 'status':None}
    camera = None

    def build(self):
        if False and platform ==  "android":
            from android import AndroidService
            service = AndroidService('desire sensors service', 'running')
            service.start('service started')
            self.service = service

        status_page = StatusPage()
        accelerometer.enable()
        compass.enable()
        self.gps = gps
        self.gps.configure(on_location=self.on_gps_location,
                           on_status=self.on_gps_status)
        self.gps.start()

        notification.notify(title="Hello",message="Just Checking")
        #vibrator.vibrate(0.2)  # vibrate for 0.2 seconds
        print("Hello World")
        status_page.gps_data = self.gps_data

#        Clock.schedule_interval(status_page.update, 1.0 / 10.0) # 10H
        Clock.schedule_interval(status_page.update, 1.0) # 1Hz
        self.camera = Camera(play=True)
        status_page.add_widget(self.camera)
        status_page.camera = self.camera

        return status_page

    @mainthread
    def on_gps_location(self, **kwargs):
        self.gps_data['location'] = ', '.join([
            '{}={}'.format(k, v) for k, v in kwargs.items()])

    @mainthread
    def on_gps_status(self, stype, status):
        self.gps_data['status'] = 'type={}\n{}'.format(stype, status)

    @mainthread
    def on_cam_texture(self, stype, status):
        print("New Texture!")

if __name__ == '__main__':
    SensorsApp().run()
