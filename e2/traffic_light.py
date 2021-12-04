from machine import Pin
import time


RED =Pin(32,Pin.OUT)
YELLOW =Pin(33,Pin.OUT)
GREEN =Pin(14,Pin.OUT)
BUTTON = Pin(36, Pin.IN)

def green():
  GREEN.on()
  RED.off()
  YELLOW.off()

def yellow():
  GREEN.off()
  YELLOW.on()
  RED.off()

def red():
  RED.on()
  YELLOW.off()
  GREEN.off()

steps = [red,yellow,green,yellow]
c = 0 

while True:
  if BUTTON.value() == 0:
    steps[c]()
    c = c +1
    if c > 3:
      c=0
  time.sleep(1)

  
  

