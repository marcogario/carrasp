try:
    import RPi.GPIO as GPIO
    rpi = True
except:
    print("Cannot import GPIO")
    rpi = False

SteeringEnablePin  = 16;
ThrottleControlPin = 12;

ThrottleDirectionPin  = 8;
SteeringDirectionPin = 10;



class SteeringDirection(object):
    LEFT = -1
    NONE = 0
    RIGHT =1


class PiPin(object):
    def __init__(self, pin_id, direction=None):
        if direction is None:
            direction = GPIO.OUT
        self.pin_id = pin_id
        self.direction = direction

        # Setup
        GPIO.setup(self.pin_id, self.direction)

    def __call__(self, value):
        gpio_value = GPIO.HIGH if value else GPIO.LOW
        GPIO.output(self.pin_id, gpio_value)

class PiWheels(object):
    """Uses the following namespace variables:

       - target_steering
       - target_throttle
       - do_quit
    """

    def __init__(self, namespace):
        self.ns = namespace
        self.current_steering = SteeringDirection.NONE
        self.current_throttle = 0

        self.throttle_direction = None
        self.throttle_control = None
        self.steering_enable = None
        self.steering_direction = None


    def setup(self):
        GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location

        # Configure GPIO's
        self.throttle_direction = PiPin(ThrottleDirectionPin)
        self.steering_direction = PiPin(SteeringDirectionPin)
        self.steering_enable = PiPin(SteeringEnablePin)

        # Reset output values
        self.throttle_direction(True)
        self.steering_enable(False)

        # PWM controller with Frequece to 1KHz
        GPIO.setup(ThrottleControlPin, GPIO.OUT)
        self.throttle_control = GPIO.PWM(ThrottleControlPin, 1000)
        self.throttle_control.start(0)

    def control_loop(self):
        print("Wheels: control_loop has started")
        while not self.ns.do_quit:
            self.update_steering(self.ns.target_steering)
            self.update_throttle(self.ns.target_throttle)
        self.shutdown()
        print("Wheels: control_loop has stopped")

    def shutdown(self):
        # Set enabled to False
        self.steering_enable(False)
        self.throttle_direction(False)

        # Stop PWM Throttle Control
        self.throttle_control.stop()

        try:
            GPIO.cleanup()
        except Exception as ex:
            print(ex)

    def update_throttle(self, target_throttle):
        # TODO: This can be made more sophisticated by using rules for
        # defining the acceleration curve
        if target_throttle != self.current_throttle:
            print("Wheels: Updating throttle to: %d" % target_throttle)
            if target_throttle >= 0:
                self.throttle_direction(False)
                self.throttle_control.ChangeDutyCycle(target_throttle)
            else:
                self.throttle_direction(True)
                self.throttle_control.ChangeDutyCycle(-target_throttle)
            self.current_throttle = target_throttle

    def update_steering(self, target_steering):
        if target_steering != self.current_steering:
            print("Wheels: Updating steering to: %d" % target_steering)
            if target_steering == SteeringDirection.LEFT:
                self.do_steer_left()
            elif target_steering == SteeringDirection.RIGHT:
                self.do_steer_right()
            else:
                assert target_steering == SteeringDirection.NONE, \
                "Unknown value %s for steering" % str(target_steering)
                self.do_steer_none()

    def do_steer_left(self):
        self.steering_enable(True)
        self.steering_direction(False)
        self.current_steering = SteeringDirection.LEFT

    def do_steer_right(self):
        self.steering_enable(True)
        self.steering_direction(True)
        self.current_steering = SteeringDirection.RIGHT

    def do_steer_none(self):
        self.steering_enable(False)
        self.steering_direction(False)
        self.current_steering = SteeringDirection.NONE


class WheelsMock(PiWheels):
    def __init__(self, namespace):
        PiWheels.__init__(self, namespace)

    def setup(self):
        pass

    def shutdown(self):
        pass

    def update_throttle(self, target_throttle):
        if target_throttle != self.current_throttle:
            print("Wheels: Updating throttle to: %d" % target_throttle)
            self.current_throttle = target_throttle

    def update_steering(self, target_steering):
        if target_steering != self.current_steering:
            print("Wheels: Updating steering to: %d" % target_steering)
            self.current_steering = target_steering

if not rpi:
    Wheels = WheelsMock
else:
    Wheels = PiWheels

#
# Simple demo to test that the hardware is working correctly
#
if __name__ == "__main__":
    import time
    class MockNamespace(object):
        target_steering = SteeringDirection.NONE
        target_throttle = 0

    ns = MockNamespace()
    w = Wheels(ns)
    print("Setup")
    w.setup()
    time.sleep(1)

    print("Steering Right")
    ns.target_steering = SteeringDirection.RIGHT
    w.update_steering(ns.target_steering)
    time.sleep(2)

    print("Steering Left")
    ns.target_steering = SteeringDirection.LEFT
    w.update_steering(ns.target_steering)
    time.sleep(2)

    print("Steering None")
    ns.target_steering = SteeringDirection.NONE
    w.update_steering(ns.target_steering)
    time.sleep(2)

    print("Throttle +50%")
    ns.target_throttle = 50
    w.update_throttle(ns.target_throttle)
    time.sleep(1)

    print("Throttle +100%")
    ns.target_throttle = 100
    w.update_throttle(ns.target_throttle)
    time.sleep(1)

    print("Throttle 0%")
    ns.target_throttle = 0
    w.update_throttle(ns.target_throttle)
    time.sleep(1)

    print("Throttle -50%")
    ns.target_throttle = -50
    w.update_throttle(ns.target_throttle)
    time.sleep(1)

    print("Throttle -10%")
    ns.target_throttle = -100
    w.update_throttle(ns.target_throttle)
    time.sleep(1)

    print("Exiting")
    w.shutdown()
