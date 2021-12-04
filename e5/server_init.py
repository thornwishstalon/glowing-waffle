#@author 0726104, Fabian Pechstein
import network
from machine import Pin,SoftI2C
import time
######################
# SETUP STUFF
######################
LED = Pin(12, Pin.OUT) 
LED.on()

time.sleep_ms(500)
import ssd1306

# display
i2c_rst = Pin(16, Pin.OUT)
i2c_rst.value(0)
time.sleep_ms(5)
i2c_rst.value(1)

i2c_sc1 = Pin(15, Pin.OUT, Pin.PULL_UP)
i2c_sda = Pin(4, Pin.OUT, Pin.PULL_UP)

i2c = SoftI2C(scl=i2c_sc1, sda=i2c_sda)
lcd= ssd1306.SSD1306_I2C(128,64,i2c)

# wifi
wlan = None

######################
# start network
######################
LED.on()
_ssid='ESP-AP'
wlan = network.WLAN(network.AP_IF) # create access-point interface
wlan.config(essid=_ssid) # set the ESSID of the access point
wlan.config(max_clients=5) # set how many clients can connect to the network
wlan.active(True)         # activate the interface
print('network ready')
LED.off()

######################
# start server
######################
from server import setup_app

print(wlan.ifconfig())
host = wlan.ifconfig()[0]
port = 80

import ulogging as logging
logging.basicConfig(level=logging.INFO)


app = setup_app(LED)

lcd.fill(0)
lcd.text("ssid:{}".format(_ssid),0,0)
lcd.text("{}:{}".format(host,port),0,20)

lcd.show()

app.run(debug=True, host = host, port= port)
## --> moved to boot.py
## add to boot py:
##   from server_init import app, host, port
##   app.run(debug=True, host = host, port= port)






