import time
from machine import ADC, Pin, PWM

# some definitions
min_freq = 1000
max_freq = 20000
max=4096
min=0

# potentiometer
input = ADC(Pin(32))
input.atten(ADC.ATTN_11DB)

# used to compute a mapping between ranges
freq_range = max_freq - min_freq  
sensor_range = max - min


def _map_reading(current_value):
  scaled_input = float(current_value - min) / float(sensor_range)
  return int( min_freq + (freq_range * scaled_input) )

# speaker
speaker = PWM(Pin(22),freq=_map_reading(input.read()))

while True:
  updated_freq= _map_reading(input.read())
  # for debug reasons
  print(updated_freq)
  speaker.freq(updated_freq)
  # sleep tight little one
  time.sleep_ms(100)
