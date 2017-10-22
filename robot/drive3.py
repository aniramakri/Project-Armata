import RPi.GPIO as gpio
import time


curr = 0
dest = 2000
cutoff = 10
Kp = 1
Kd = 0.6
Ki = 0

def init():
    gpio.setmode(gpio.BOARD)
    gpio.setup(13, gpio.OUT)
    gpio.setup(15, gpio.OUT)
    gpio.setup(7, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.setup(11, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.add_event_detect(7, gpio.FALLING, callback=encoderCB)
    gpio.add_event_detect(11, gpio.FALLING, callback=encoderCB)

def encoderCB(channel):
    global curr
    if channel == 7:
        if (gpio.input(7) ^ gpio.input(11) == 0):
            curr += 1
        else:
            curr -= 1
    if channel == 11:
        if (gpio.input(7) ^ gpio.input(11) == 1):
            curr += 1
        else:
            curr -= 1

def clip(diff):
    if diff > 100:
        return 100
    elif diff < -100:
        return -100
    else:
        return diff

def rot(duty):
    output13 = False
    output15 = False
    if duty == 0:
        return
    elif duty < 0:
        output13 = True
    else:
        output15 = True
    T = float(abs(duty)) / 1000
    gpio.output(13, output13)
    gpio.output(15, output15)
    time.sleep(T)
    gpio.output(13, False)
    gpio.output(15, False)
    time.sleep(0.1 - T) # 100% duty cycle, divided by 1000

def forward(steps):
    init()
    prevErr = 0
    iErr = 0
    while abs(curr - steps) > cutoff:
        pErr = steps - curr
        dErr = pErr - prevErr
        iErr += pErr
        pidOut = (Kp * pErr) + (Kd * dErr) + (Ki * iErr)
        clippedErr = clip(pidOut)
        rot(clippedErr)
        prevErr = pErr
    gpio.cleanup()

forward(dest)
