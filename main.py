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

# One pixel connected internally!
dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.1)

# Built in red LED
# led = DigitalInOut(board.D13)
# led.direction = Direction.OUTPUT
led = pulseio.PWMOut(board.D13, frequency=5000, duty_cycle=0)
led2 = pulseio.PWMOut(board.D2, frequency=5000, duty_cycle=0)

button = DigitalInOut(board.D3)
button.direction = Direction.INPUT
button.pull = Pull.UP

# Analog output on D1
aout = AnalogOut(board.D1)

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

i = 0
led_duty = 0
led2_duty = 50

button_down = False
button_down_cycles = 0
circle_direction = 1

while True:
    # spin internal LED around! autoshow is on
    dot[0] = wheel(i & 255)

    # set analog output to 0-3.3V (0-65535 in increments)
    aout.value = i * 256

    if led_duty < 50:
        led.duty_cycle = int(led_duty * 65535 / 50)  # Up
    else:
        led.duty_cycle = 65535 - int((led_duty - 50) * 65535 / 50)  # Down
    #print(str(led_duty) + " " + str(led.duty_cycle))

    if led2_duty < 50:
        led2.duty_cycle = int(led2_duty * 65535 / 50)  # Up
    else:
        led2.duty_cycle = 65535 - int((led2_duty - 50) * 65535 / 50)  # Down


    if not button.value:
        if not button_down:
            button_down = True
            print("Button on D2 pressed!")
        else:
            led.duty_cycle = 65535
            button_down_cycles = button_down_cycles + 1
    if button.value and button_down:
        button_down = False
        print(button_down_cycles)
        button_down_cycles = 0
        circle_direction = circle_direction * -1

    led_duty = (led_duty+1) % 100  # run from 0 to 255
    led2_duty = (led2_duty+1) % 100  # run from 0 to 255
    i = (i+circle_direction) % 256  # run from 0 to 255
    if i < 0:
        i = 255
    time.sleep(0.01)  # make bigger to slow down