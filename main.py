import state_machine.cat_door_state_machine as state
import time
import logging
from logging.handlers import TimedRotatingFileHandler

if __name__ == "__main__":
    logger = logging.getLogger('logger_util')
    logger.setLevel(logging.DEBUG)
     # create file handler which logs even debug messages
    fh = logging.FileHandler('log/cat_door.log')
    fh.setLevel(logging.DEBUG)
     # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
     # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    rollover_handler = TimedRotatingFileHandler(
    'logger_util',
    when="midnight",
    interval=1,
    backupCount=7
)
     # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.addHandler(rollover_handler)
    current_state = 'Init'
    first_call = True
    state_dict = state.get_class_dict()
    try:
          while True:

               try:
                  new_state = state_dict[current_state].do_state(first_call)
                  if new_state == current_state:
                       first_call = False 
                  else:
                       first_call = True
                       current_state = new_state
                       logger.info(f'changing state to {new_state}')
               except KeyError as KE:
                    logger.error(f"key not found: {new_state}")
               time.sleep(.1)
    except KeyboardInterrupt:
           print("Shutting down")
           state.Init.doCleanup()           





