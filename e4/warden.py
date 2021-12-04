#@author 0726104, Fabian Pechstein
import time
from machine import ADC, Pin, PWM, SoftI2C, Timer

time.sleep_ms(500)
import ssd1306
from hcsr04 import HCSR04
from kty81222 import kty81222

#####################
# timespan in ms of how long no movement has to be detected until the alarm turns off
ALARM_TIME_SPAN = 5000
# track how many ms since last movement detection have gone by
time_since_last_movement = 0 

ALERT_DISTANCE = 20


# init for laterz
# siren 
speaker = None

# some timers
move_timer = Timer(3)
temp_timer = Timer(2)
siren_timer = Timer(1)

# used to control the siren sounds
pattern = [
  1000,3000,3000,5000,5000,3000,3000,3000,1000,1000
  ]
  
#used to control siren pattern
pattern_index = 0
# used to flag active siren
sound_flag = 0


# led PINS
green = Pin(12, Pin.OUT)
red = Pin(13, Pin.OUT)

# keep track of alert states
STATE = 0

#MARK INIT
green.on()
red.on()


# temperature
temp = ADC(Pin(32))
# pin must be between 0 and 1V

# temp sensor logic - look at kty81222.py
t_sensor = kty81222(
  analog_volt_limit=1.,
  analog_read_limit=4095,
  sensor_vdd=5.,
  sensor_r= 10000 # resistance in ohm used on board
  )

# distance sensor
sensor_distance = HCSR04(trigger_pin=14, echo_pin=23, echo_timeout_us=10000)  

# display
i2c_rst = Pin(16, Pin.OUT)
i2c_rst.value(0)
time.sleep_ms(5)
i2c_rst.value(1)

i2c_sc1 = Pin(15, Pin.OUT, Pin.PULL_UP)
i2c_sda = Pin(4, Pin.OUT, Pin.PULL_UP)

i2c = SoftI2C(scl=i2c_sc1, sda=i2c_sda)
lcd=ssd1306.SSD1306_I2C(128,64,i2c)

##############################
# callbacks 

def non_alert():  
  """show the non-alert output on display"""
  global speaker
  if speaker:
    speaker.deinit()
  red.off()
  green.on()
  
  lcd.fill(0)
  temperature = t_sensor.get_temp()
  lcd.text("TEMP: {} C".format(round(temperature,1)),0,0)
  lcd.show()

def alert_state():
  """show alert state on display"""
  global STATE
  global speaker
  global time_since_last_movement
 
  green.off()
  red.on()
  
  lcd.fill(0)
  c= (int)((ALARM_TIME_SPAN - time_since_last_movement ) / 1000)
  lcd.text("INTRUDER ALERT!!!",0,0)
  lcd.text("cooldown in {}s".format(c),0,32)
  lcd.show()

def siren_step(timer:Timer):
    """ play one note of the pattern at current position of the pattern_index; updates the index"""
    global pattern_index
    global speaker
    global pattern
    global sound_flag
    
    speaker.freq(pattern[pattern_index])
    pattern_index+=1
    
    if pattern_index == len(pattern)-1:
      #print("kill timer")
      pattern_index = 0
      sound_flag = 0 
      timer.deinit()  
  
def sound_alarm():
    """ starts a timer to play 10 notes of the sound pattern. dies after 1s"""
    global speaker
    global time_since_last_movement
    global sound_flag
    
    if(time_since_last_movement%1000 == 0 and sound_flag == 0 ):
      speaker = PWM(Pin(17),freq=1000)
      sound_flag = 1
      siren_timer.init(period=100, mode=Timer.PERIODIC, callback=siren_step)    

def temp_update(timer:Timer):
  """update the temperature buffer"""
  t_sensor.update_buffer(temp.read())

def distance_update(timer:Timer):
  """checks for movement and acts accordingly. triggers display and sound changes"""
  global STATE 
  global time_since_last_movement
  #print(STATE)
  distance = (int)( sensor_distance.distance_cm())  
  if STATE == 0 and ( distance <= ALERT_DISTANCE and distance > 0):
    #print("movement detected")
    STATE = 1   
    time_since_last_movement = 0 
  elif STATE == 1 and ( distance <= ALERT_DISTANCE and distance > 0):
    #print("movement still detected")
    time_since_last_movement = 0 
  elif STATE == 1 and ( distance > ALERT_DISTANCE):  
    time_since_last_movement+=100
    #print("no movement detected")
    
  if STATE==1 and time_since_last_movement >= ALARM_TIME_SPAN:
    STATE = 0
    non_alert()
    #print("safe")
  elif STATE == 1:
    sound_alarm()
    alert_state()
    #print("sound the alarm")
  

################################    
#  INIT DONE
################################
# Let's roll
green.off()
red.off()

# schedule updates
temp_timer.init(period=100, mode=Timer.PERIODIC, callback=temp_update )
move_timer.init(period=100, mode=Timer.PERIODIC, callback=distance_update )
















