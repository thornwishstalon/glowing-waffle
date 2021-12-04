#@author 0726104, Fabian Pechstein
import time
from machine import Pin,Timer
time.sleep_ms(500)
import urequests
import utime
import gc
from hcsr04 import HCSR04
from uuid import uuid4
import ulogging as logging

# timers  
fetch_timer = Timer(2)
led_timer = Timer(1)

# some PIN configs
led = Pin(5, Pin.OUT)
button = Pin(14, Pin.IN)
sensor_distance = HCSR04(trigger_pin=0, echo_pin=4, echo_timeout_us=10000)  

# default values & configs
distance = -1
_ssid='ESP-AP'
_token = uuid4()

logging.basicConfig(level=logging.INFO)

log = None
log_level = 1

if log_level >= 0:
  import ulogging
  log = ulogging.getLogger("client")
  if log_level > 0:
    log.setLevel(ulogging.DEBUG)  

wlan = None

##############################################################
## MIGHTY FUNCTIONS
##############################################################

## connect to network
def do_connect():
  import network
  global wlan
  wlan = network.WLAN(network.STA_IF)
  ## ran into weird issues unless i tried to connect without that first
  wlan.disconnect()
  wlan.active(False)
  ## end comment
  wlan.active(True)
  wlan.connect(_ssid)
  if not wlan.isconnected():
    if log_level > 0:
      log.debug('%.3f: connecting to "%s"' % (utime.time(), _ssid))
    while not wlan.isconnected():
      pass
      
  if log_level > 0:
      log.debug('%.3f: connected to "%s"' % (utime.time(), _ssid))
      log.debug('%.3f: network config: "%s"' % (utime.time(), wlan.ifconfig()))
  led.on()
  time.sleep_ms(1000)
  led.off()    

def distance_update():
  # was originally a timer callback
  global distance
  distance = (int)(sensor_distance.distance_cm())  

##############################################################
## client's communication skills:
##############################################################
def fetch_server_state(timer:Timer):
  global distance
  if log_level > 0:
    log.debug('%.3f: fetching server state for id: "%s"' % (utime.time(), _token))
  
  response_ref = None
  try:  
    url = 'http://192.168.4.1/state'
    headers = {'Authorization': 'Bearer {}'.format(_token),'Connection': 'Close'}
    response_ref = urequests.get(url=url, headers=headers)
    if response_ref.status_code == 200:
      response = response_ref.json()
      if log_level > 0:
        log.info('%.3f: server state: %s' % (utime.time(), response))
      if (int)(response['door']) != button.value() or (int)(response['distance']) != distance:
        if log_level > 0:
          log.info('%.3f: server has differnt values than client' % (utime.time()))
        return
      if response['action'] == 1:
        led.on()        
        led_timer.init(period=3000, mode=Timer.ONE_SHOT, callback=lambda t:led.off())
    else:
       log.error('%.3f: server response was HTTP STATUS"%s"' % (utime.time(), response_ref.status_code))
  except Exception as e:
    log.error('%.3f: exception occured: "%s"' % (utime.time(), e))

  finally:
    # socket clean up
    if response_ref:
      response_ref.close()


def push_client_state(p):
  global distance
  distance = (int)( sensor_distance.distance_cm())  
  if log_level > 0:
    log.debug('%.3f: pushing client state for id: "%s"' % (utime.time(), _token))
  
  response_ref = None
  try:
    url = 'http://192.168.4.1/state?distance=%s&door=%s' % (distance, button.value())    
    headers = {'Authorization': 'Bearer {}'.format(_token),'Connection': 'Close'}
    response_ref = urequests.put(url=url, headers=headers)
    if response_ref.status_code == 200:
      # nothing to do here
      pass
    else:
      # oh boy!
      log.error('%.3f: server response was HTTP STATUS"%s"' % (utime.time(), response_ref.status_code))
  except Exception as e:
    log.error('%.3f: exception occured: "%s"' % (utime.time(), e))  
  finally:
    # socket clean up
    if response_ref:
      response_ref.close()
  
##############################################################
## END FUNCTIONS
##############################################################  

##############################################################
## connect to the server's network
do_connect()  
if log_level >= 1:
  log.info('%.3f: network ready: "%s"' % (utime.time(), _ssid))

##############################################################
## do some housekeeping before the main tasks starts
if log_level > 0:
  log.debug('%.3f: calling gc.collect' % (utime.time()))
  
gc.collect()
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

##############################################################
## noice! 
## now to main works
##############################################################

if log_level > 0:
  log.debug('%.3f: client_id is: "%s"' % (utime.time(), _token))
  log.debug('%.3f: pushing intial state to server' % (utime.time()))

# register initial state!
distance_update()
push_client_state(None)


###### TIMERS
fetch_timer.init(period=5000, mode=Timer.PERIODIC, callback=fetch_server_state )

## interrupts on "door"-change
button.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=push_client_state)


