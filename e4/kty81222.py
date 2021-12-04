
#@author 0726104, Fabian Pechstein
class kty81222:
  # temp and sensor resistance - see datasheet: 
  # https://cdn-reichelt.de/documents/datenblatt/C650/KTY81_SER.pdf
  characteristics_table = [
    [-55, 990.,0],
    [-50, 1040.,0],
    [-40, 1116.,0],
    [-30, 1260.,0],
    [-20, 1381.,0],
    [-10, 1510.,0],
    [0, 1646.,0],
    [10, 1790.,0],
    [20, 1941.,0],
    [25, 2020.,0],
    [30, 2100.,0],
    [40, 2267.,0],
    [50, 2441.,0],
    [60, 2623.,0],
    [70, 2812.,0],
    [80, 3009.,0],
    [90, 3214.,0],
    [100, 342.6,0],
    [110, 3643.,0],
    [120, 3855.,0],
    [125, 3955.,0],
    [130, 4048.,0],
    [140, 4208.,0],
    [150, 4323.,0]
  ]
  
  sensor_vdd= 5.
  sensor_r = 3300 #  
  analog_volt_limit = 1.
  analog_read_limit = 4095
  ring_buffer = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
  ring_buffer_size = 20
  buffer_index = 0
  buffer_warm = False
  
  def __init__(self, 
    sensor_vdd= 5.,
    sensor_r = 10000,  
    analog_volt_limit = 1.,
    analog_read_limit = 4095
    ):
    self.sensor_vdd= sensor_vdd
    self.sensor_r = sensor_r
    self.analog_volt_limit = analog_volt_limit
    self.analog_read_limit = analog_read_limit
  
  def update_buffer(self, reading):
    self.ring_buffer[self.buffer_index] = self._temp_from_reading(reading)
    self.buffer_index = self.buffer_index + 1
    if self.buffer_index >= self.ring_buffer_size:
      self.buffer_warm = True
      self.buffer_index = 0
  
  def get_temp(self):
    if self.buffer_warm:
      return sum(self.ring_buffer) / len(self.ring_buffer)
    
    return 999
 
  def _temp_from_reading(self, read):
    u_t = (float)( self.analog_volt_limit / self.analog_read_limit) * (float)(read) + 0.02 # measurment was a little bit off for whatever reason - checked with multimeter
    r_t = (u_t/ (float)(self.sensor_vdd - u_t)) * self.sensor_r
    return self._get_temp(r_t)
  
  def _map_reading(self, current_value, min, max, t_min, t_max):
    scaled_input = float(current_value - min) / float((max - min))
    return t_min + ((t_max - t_min) * scaled_input)
  
  def _get_temp(self, reading):
    for i in range(0,len(self.characteristics_table)-1):
      p = self.characteristics_table[i]
      p_plus = self.characteristics_table[i+1]

      if reading >= p[1] and reading <= p_plus[1]:
        # interpolate
        return self._map_reading(reading, p[1],p_plus[1], p[0], p_plus[0])
    
    return None

