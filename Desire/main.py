from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock, mainthread
from kivy.utils import platform
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.camera import Camera

from plyer import vibrator, tts, notification
from plyer import accelerometer, battery, compass, gps


class StatusPage(Widget):
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


class SensorsApp(App):
    service = None
    gps = None
    gps_data = {'location':None, 'status':None}

    def build(self):
        if platform ==  "android":
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


        button=Button(text='Service',size_hint=(0.12,0.12))
        button.bind(on_press=self.callback)
        status_page.add_widget(button)

        switch = Switch()
        switch.bind(active=self.callback)
        status_page.add_widget(switch)
        return status_page

    def on_stop(self):
        if self.service is not None:
            print("Stopping Desire Service")
            self.service.stop()

    def callback(self, instance, value):
        print('the switch', instance, 'is', value)



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
