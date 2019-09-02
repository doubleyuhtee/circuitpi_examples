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
    MAX_VALUE = 255
    DELAY = 3
    STATE_DURATION = 55
    def __init__(self, pin):
        self.aout = AnalogOut(pin)
        self.increment = -1
        self.states = [
            {
                'brightness': 223
            },
            {
                'brightness': 239
            },
            {
                'brightness': AnalogLed.MAX_VALUE
            }
        ]
        self.state_index = 0
        self.state = self.states[self.state_index]
        self.delay = AnalogLed.DELAY
        self.state_duration = AnalogLed.STATE_DURATION
        self.value = AnalogLed.MAX_VALUE
        self.aout.value = AnalogLed.MAX_VALUE

    def adjust_brightness_factor(self):
        self.state_index = self.state_index + 1
        if self.state_index >= len(self.states):
            self.state_index = 0
        self.state = self.states[self.state_index]
        self.aout.value = self.value * 256  # Max current brightness
        self.increment = -1
        self.state_duration = 65


    def run(self):
        if self.delay == 0:
            self.delay = AnalogLed.DELAY
            self.state_duration = self.state_duration - 1
            if self.state_duration == 0:
                self.increment = self.increment * -1
                self.state_duration = AnalogLed.STATE_DURATION
            self.value = self.value + self.increment
            self.aout.value = self.value * self.state['brightness']
        else:
            self.aout.value = self.value * self.state['brightness']
        self.delay = self.delay - 1



class TwinkleLed:
    def __init__(self, led: Led):
        self.led = led
        self.state_duration = 1
        self.states = [
            {
                'brightness': 50,
                'min_duration': 100,
                'max_duration': 1000
            },
            {
                'brightness': 150,
                'min_duration': 50,
                'max_duration': 500
            },
            {
                'brightness': 250,
                'min_duration': 30,
                'max_duration': 200
            }
        ]
        self.current_state = self.states[0]

    def run(self):
        self.state_duration = self.state_duration - 1
        if self.state_duration == 0:
            self.current_state = random.choice(self.states)
            self.state_duration = random.randint(self.current_state['min_duration'],
                                                 self.current_state['max_duration'])
        self.led.set_brightness(self.current_state['brightness'])


# One pixel connected internally!
dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.4)

led1 = TwinkleLed(Led(board.D13))
led2 = TwinkleLed(Led(board.D4))
led3 = TwinkleLed(Led(board.D2))
led4 = TwinkleLed(Led(board.D0))

button = DigitalInOut(board.D3)
button.direction = Direction.INPUT
button.pull = Pull.UP

# Analog output on D1
aled = AnalogLed(board.D1)

# HELPERS #

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
    aled.run()

    if not button.value:
        if not button_down:
            button_down = True
            BRIGHTNESS_FACTOR = BRIGHTNESS_FACTOR + 32
            if BRIGHTNESS_FACTOR > 256:
                BRIGHTNESS_FACTOR = 32
            aled.adjust_brightness_factor()
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