# Trinket IO demo
# Welcome to CircuitPython 3.1.1 :)
import array
import board
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogOut, AnalogIn
import touchio
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import adafruit_dotstar as dotstar
import time
import neopixel
import pulseio
import random

BRIGHTNESS_FACTOR = 32

class Led:
    def __init__(self, pin):
        self.led = pulseio.PWMOut(pin, frequency=5000, duty_cycle=0)
        self.brightness = 0

    def set_brightness(self, brightness):
        self.brightness = brightness
        self.led.duty_cycle = brightness * BRIGHTNESS_FACTOR

    def adjust_brightness(self, increment):
        self.brightness = self.brightness + increment
        self.led.duty_cycle = self.brightness * BRIGHTNESS_FACTOR

class AnalogLed:
    def __init__(self, pin):
        self.aout = AnalogOut(pin)
        self.brightness = 65535
        self.aout.value = self.brightness

    def set_brightness(self, brightness):
        self.brightness = brightness
        print(self.brightness)
        self.aout.value = brightness * 256

    def adjust_brightness(self, increment):
        self.brightness = self.brightness + increment
        self.aout.value = self.brightness * 256


class AmbientLight:
    def __init__(self, led):
        self.led = led
        self.increment = -2
        self.led.set_brightness(512)
        self.state_duration = 250

    def run(self):
        self.state_duration = self.state_duration - 1
        if self.state_duration == 0:
            self.increment = self.increment * -1
            self.state_duration = 500
        self.led.adjust_brightness(self.increment)


class TwinkleLed:
    def __init__(self, led: Led):
        self.led = led
        self.state_duration = random.randint(10, 1000)
        self.state = 50
        self.next_state = 800

    def run(self):
        self.state_duration = self.state_duration - 1
        if self.state_duration == 0:
            self.state_duration = random.randint(10,100)
            swap = self.state
            self.state = self.next_state
            self.next_state = swap
        self.led.set_brightness(self.state)


# One pixel connected internally!
dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.4)

led1 = AmbientLight(Led(board.D13))
led2 = AmbientLight(Led(board.D4))
led3 = TwinkleLed(Led(board.D2))
led4 = TwinkleLed(Led(board.D0))

button = DigitalInOut(board.D3)
button.direction = Direction.INPUT
button.pull = Pull.UP

# Analog output on D1
aled = AnalogLed(board.D1)

# HELPERS #
# Helper to convert analog input to voltage
def getVoltage(pin):
    return (pin.value * 3.3) / 65536

# Helper to give us a nice color swirl
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if (pos < 0):
        return (0, 0, 0)
    if (pos > 255):
        return (0, 0, 0)
    if (pos < 85):
        return (int(pos * 3), int(255 - (pos*3)), 0)
    elif (pos < 170):
        pos -= 85
        return (int(255 - pos*3), 0, int(pos*3))
    else:
        pos -= 170
        return (0, int(pos*3), int(255 - pos*3))



# MAIN LOOP #
button_down = False
button_down_cycles = 0
circle_direction = 1
i=0
while True:
    # spin internal LED around! autoshow is on
    dot[0] = wheel(i & 255)

    led1.run()
    led2.run()
    led3.run()
    led4.run()
    aled.set_brightness(i)

    if not button.value:
        if not button_down:
            button_down = True
            print("Button on D2 pressed!")
        else:
            button_down_cycles = button_down_cycles + 1
    if button.value and button_down:
        button_down = False
        print(button_down_cycles)
        button_down_cycles = 0
        circle_direction = circle_direction * -1

    i = (i+circle_direction) % 256  # run from 0 to 255
    if i < 0:
        i = 255
    time.sleep(0.01)  # make bigger to slow down