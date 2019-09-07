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

class Led:
    def __init__(self, pin):
        self.led = pulseio.PWMOut(pin, frequency=5000, duty_cycle=0)
        self.brightness = 0

    def set_brightness(self, brightness):
        self.brightness = brightness
        self.led.duty_cycle = brightness

    def adjust_brightness(self, increment):
        self.brightness = self.brightness + increment
        self.led.duty_cycle = self.brightness

class PulseLed:
    MAX_VALUE = 255
    DELAY = 1
    STATE_DURATION = 254
    states = [
        {
            'brightness': 40
        },
        {
            'brightness': 100
        },
        {
            'brightness': MAX_VALUE
        }
    ]
    def __init__(self, led):
        self.led = led
        self.increment = -1
        self.state_index = 0
        self.state = PulseLed.states[self.state_index]
        self.delay = PulseLed.DELAY
        self.state_duration = PulseLed.STATE_DURATION
        self.value = PulseLed.MAX_VALUE

    def run(self):
        self.delay = PulseLed.DELAY
        self.state_duration = self.state_duration - 1
        if self.state_duration == 0:
            self.increment = self.increment * -1
            self.state_duration = PulseLed.STATE_DURATION
        self.value = self.value + self.increment
        self.led.set_brightness(self.value * self.state['brightness'])

    def advance_state(self):
        self.state_index = self.state_index + 1
        if self.state_index >= len(PulseLed.states):
            self.state_index = 0
        self.state = PulseLed.states[self.state_index]
        self.value = PulseLed.MAX_VALUE
        self.state_duration = PulseLed.STATE_DURATION
        self.increment = -1


class TwinkleLed:
    multiplier = 255

    def __init__(self, led: Led):
        self.led = led
        self.state_duration = 1
        self.states = [
            {
                'brightness': 20,
                'min_duration': 100,
                'max_duration': 1000
            },
            {
                'brightness': 100,
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
        self.led.set_brightness(self.current_state['brightness'] * TwinkleLed.multiplier)

    @staticmethod
    def update_brighness_range():
        TwinkleLed.multiplier = TwinkleLed.multiplier + 32
        if TwinkleLed.multiplier > 256:
            TwinkleLed.multiplier = 32

    def recalculate_brightness(self):
        self.led.set_brightness(self.current_state['brightness'] * TwinkleLed.multiplier)

        
class AnalogButton:
    def __init__(self, pin):
        self.analog_in = AnalogIn(pin)

    def down(self):
        return self.analog_in.value < 200

# One pixel connected internally!
dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.4)

button = AnalogButton(board.D1)

twinkle1 = TwinkleLed(Led(board.D13))
twinkle2 = TwinkleLed(Led(board.D4))
twinkle3 = TwinkleLed(Led(board.D2))
twinkle4 = TwinkleLed(Led(board.D0))
pulse1 = PulseLed(Led(board.D3))

# button = DigitalInOut(board.D3)
# button.direction = Direction.INPUT
# button.pull = Pull.UP


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
skip = 5

while True:
    # spin internal LED around! autoshow is on
    skip = skip - 1
    if skip == 0:
        dot[0] = wheel(i & 255)
        skip = 5
        i = (i+circle_direction) % 256  # run from 0 to 255
        if i < 0:
            i = 255


    twinkle1.run()
    twinkle2.run()
    twinkle3.run()
    twinkle4.run()
    pulse1.run()

    if button.down():
        if not button_down:
            button_down = True
            pulse1.advance_state()
            TwinkleLed.update_brighness_range()
            twinkle1.recalculate_brightness()
            twinkle2.recalculate_brightness()
            twinkle3.recalculate_brightness()
            twinkle4.recalculate_brightness()
            print("Button on D2 pressed!")
        else:
            button_down_cycles = button_down_cycles + 1
    if not button.down():
        button_down = False
        button_down_cycles = 0
        circle_direction = circle_direction * -1
    time.sleep(0.01)  # make bigger to slow down