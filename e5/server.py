import picoweb
from machine import Pin
import ujson
import utime

import ulogging as logging
logging.basicConfig(level=logging.INFO)

log = None
log_level = 1

if log_level >= 0:
  import ulogging
  log = ulogging.getLogger("picoweb")
  if log_level > 0:
    log.setLevel(ulogging.DEBUG)
  log = log


class NotFoundException(Exception):
  pass
class ParametersMissingException(Exception):
  pass


class ClientState():
  DISTANCE_LABEL= "distance"
  DOORSTATE_LABEL= "door"
  ACTION_LABEL= "action"
  
  action_distance = 10
  timestamp_updated = None
  distance = -1.
  door_state = -1
  
  @property
  def action(self):
    if self.distance < self.action_distance:
      return 1
    return 0
    
  def __init__(self,action_distance=10):
    self.action_distance=action_distance
  
  def update(self, distance:int, door_state:int):
    self.timestamp_updated = utime.time()
    self.distance = distance
    self.door_state = door_state
    return self
  
  def to_json(self):
    return {
      ClientState.DISTANCE_LABEL: self.distance,
      ClientState.DOORSTATE_LABEL: self.door_state,
      ClientState.ACTION_LABEL: self.action
    }
     
    
class ServerState():  
  client_state = {}
  
  def get_client_state(self, client_id:str)-> ClientState:
    if log_level > 0:
      log.debug('%.3f: retrieve state of "%s"' % (utime.time(), client_id))
    if client_id in self.client_state.keys():
      return self.client_state[client_id]
      
    if log_level > 0:
      log.debug('%.3f: state of "%s" unavailable' % (utime.time(), client_id))      
    raise NotFoundException()
  
  def update_client_state(self,client_id:str, state:ClientState):
    if log_level > 0:
      log.debug('%.3f: persist state of "%s"' % (utime.time(), client_id))
    self.client_state[client_id] = state
     
    
def setup_app(LED:Pin, debug=-1)->picoweb.WebApp:

  
  state = ServerState()
  app = picoweb.WebApp(__name__)
  
  def require_auth(func):
    def auth(req, resp):
        auth = req.headers.get(b"Authorization")
        if log_level > 0:
          log.debug('%.3f: checking authorization"' % (utime.time()))
        
        if not auth:
            yield from picoweb.http_error(resp, "401")
            return
        # assume everything is utf-8 encoded!
        auth =auth.decode('utf-8')
        req.token = auth.replace('Bearer','').strip()
        if log_level > 0:
          log.debug('%.3f: granted to "%s"' % (utime.time(), req.token))
        
        yield from func(req, resp)

    return auth
  
  def flash(func):
    def flash(req, resp):
      LED.on()
      yield from func(req, resp)
      LED.off()
    return flash 
  
  def _parse_query_string(qs):    
    parameters = {}
    if qs:
      ampersandSplit = qs.split("&") 
      for element in ampersandSplit:
        equalSplit = element.split("=")
        parameters[equalSplit[0]] = equalSplit[1]
     
    return parameters
  
  def _require_parameters(elements, required):
    for r in required:
      if r not in elements.keys():
        raise ParametersMissingException()
  
  @app.route("/state")
  @flash
  @require_auth
  def state_route(req, resp):
    if req.method == "GET":
      try:
        client_state = state.get_client_state(req.token)
        encoded = ujson.dumps(client_state.to_json())
        yield from picoweb.start_response(resp, content_type = "application/json")
        yield from resp.awrite(encoded)
      except NotFoundException:        
        yield from picoweb.http_error(resp, "404")        
    elif req.method == "PUT":
        try:          
          parameters= _parse_query_string(req.qs)
          _require_parameters(parameters, [ClientState.DISTANCE_LABEL, ClientState.DOORSTATE_LABEL])
          client_state = None
          try: 
            client_state = state.get_client_state(req.token)
          except NotFoundException:
            client_state = ClientState()
                      
          state.update_client_state(
            req.token, 
            client_state.update(
              distance=(int)(parameters[ClientState.DISTANCE_LABEL]),
              door_state=(int)(parameters[ClientState.DOORSTATE_LABEL])
            )
          )
          encoded = ujson.dumps({'state':"ok"})
          
          yield from picoweb.start_response(resp, content_type = "application/json")
          yield from resp.awrite(encoded)      
        except ParametersMissingException:        
          yield from picoweb.http_error(resp, "400")        
        
    else:        
      yield from picoweb.http_error(resp, "405")

 
  return app
  



