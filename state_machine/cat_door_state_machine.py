from abc import ABC, abstractmethod
import time
import IO.RaspPI_IO
import ML.IdentifyCat 
import email_comm.email_results as em
import camera.camera
import Util.config_data
import sys
from datetime import datetime
import logging





def get_class_dict():
    state_dict = {}
    state_dict['Init'] = Init()
    state_dict['DoorClosed'] = DoorClosed()
    state_dict['Evaluate'] = Evaluate()
    state_dict['DoorOpening'] = DoorOpening()
    state_dict['DoorOpened'] = DoorOpened()
    state_dict['DoorClosing'] = DoorClosing()
    state_dict['Error'] = Error()
    return state_dict


class DoorState(ABC):
    """
    base class to be extended for each door state
    """

    """
    each state implements its own version of this class.
    These are the activities that the state undertakes upon entry
    (essentially business logic for the cat door)
    """
    def __init__(self):
        self.logger = logging.getLogger('logger_util.DoorState')
        self.logger.info('creating an instance of logger for door states')
        self.cd = Util.config_data.ConfigUtility()
        self.email = em.SendEmail(self.cd)
        self.cat_id = ML.IdentifyCat.IDCat(self.cd)
        self.cam = camera.camera.Cam(self.cd)
        self.RP = IO.RaspPI_IO.RaspPi_IO()
        self.DOOR_OPEN_TIMEOUT = self.cd.get_config("DOOR_OPEN_TIMEOUT")
        self.DOOR_CLOSE_TIMEOUT = self.cd.get_config("DOOR_CLOSE_TIMEOUT")
        self.DOOR_MOVEMENT_TIMEOUT = self.cd.get_config("DOOR_MOVEMENT_TIMEOUT")
        self.DOOR_OPEN_DWELL = self.cd.get_config("DOOR_OPEN_DWELL")
        self.bypass = self.cd.get_config("BYPASS_ID_RESULT")
        self.cat_name = self.cd.get_config("CAT_NAME")
        self.dir = self.cd.get_config("PHOTO_LOCATION")
        self.log_lcn= self.cd.get_config("LOG_LOCATION")
    
    @abstractmethod
    def do_state(self,first_call):
        pass

    @classmethod 
    def doCleanup(cls):
        RP = IO.RaspPI_IO.RaspPi_IO()
        RP.cleanup()

class Init(DoorState):
    """
    do these things when the init state is started.
    """
    
    def do_state(self, first_call):
        if first_call:
            self.logger.info('Entered State: Init')
        if self.RP.get_io_status("door_closed_ls"):
            return 'DoorClosing'
        else:
            return 'DoorClosed'


class DoorClosed(DoorState):
    """
    do these things when the init state is started.
    """

    def do_state(self, first_call):
        if first_call:
            self.logger.info('Entered State: Door Closed')
        if not self.RP.get_io_status("prox"):
            return 'Evaluate'
        if not self.RP.get_io_status("open_pb"):
            return 'DoorOpening'
        return 'DoorClosed'


class Evaluate(DoorState):
    """
    do these things when the init state is started.
    """

    def do_state(self , first_call):
        if first_call:
            self.logger.info('Entered State: Evaluate')
        # take photos
        self.cam.take_photos()
        # is this my cat?
        decision = self.cat_id.id_cat()
        now = datetime.now()
        format_time = now.strftime("%H:%M:%S")
        """
        Bypass configuration: 
        0 --> most permissive. Will always open door regardless of whether or not a cat was identified in any photo
        1 --> medium permissive. at least one photo must have identified a cat, but not necessarily the cat that the model was trained on.
        2 --> most restrictive. at least one photo must have identified the cat the model was trained on.
        """
        if decision <= self.bypass:
          body = f"Door Activated {format_time} - criteria met"
        else:
          body = f"Door NOT Activated  {format_time} - criteria not met"     

        # send email
        self.email.email_photos(body, self.cat_name,self.dir)
        if decision:
            return 'DoorOpening'
        else:
           return 'DoorClosed'
        
        


class DoorOpening(DoorState):
    """
    do these things when the init state is started.
    """

    def do_state(self, first_call):
        if first_call:
            self.start_time = time.time()
            # motor on to open door
            self.RP.set_io_command('motor_forward', 'on')
        self.run_time = time.time()

        if not self.RP.get_io_status("close_pb"):
            self.RP.set_io_command('motor_forward', 'off')
            self.logger.warning("Close PB used while door opening")
            return 'DoorClosing'
        
        if (self.run_time - self.start_time) > self.DOOR_MOVEMENT_TIMEOUT and not self.RP.get_io_status('door_closed_ls'):
           
            self.logger.error(f"Door start open timeout - no movement after {self.DOOR_MOVEMENT_TIMEOUT} seconds")
            self.RP.set_io_command('motor_forward', 'off')
            return 'Error'
        
        if (self.run_time - self.start_time) > self.DOOR_OPEN_TIMEOUT and not self.RP.get_io_status('door_open_ls'):
            self.logger.error(f"Door start open timeout - door not opened after {self.DOOR_OPEN_TIMEOUT} seconds")
            self.RP.set_io_command('motor_forward', 'off')
            return 'Error'
        
        if not self.RP.get_io_status("door_open_ls"):
            self.logger.info(f"door successfully opened after {(self.run_time - self.start_time):.2f} seconds")
            self.RP.set_io_command('motor_forward', 'off')
            self.logger.info("motor fwd turned off")
            return 'DoorOpened'
        return 'DoorOpening'
    


class DoorOpened(DoorState):
    """
    do these things when the init state is started.
    """

    def do_state(self, first_call):
        if first_call:
            self.logger.info("Entered state: door opened")
            self.start_time = time.time()
        self.run_time = time.time()
        # once door is opened wait x seconds and then begin closing
        if (self.run_time - self.start_time) > self.DOOR_OPEN_DWELL:
           self.logger.info(f"Door begins closing after {(self.run_time - self.start_time):.2f} seconds")
           return 'DoorClosing'
        
        if not self.RP.get_io_status("close_pb"):
           self.RP.set_io_command('motor_forward', 'off')
           self.logger.warning("Close PB used while door opened")
           return 'DoorClosing'
        return 'DoorOpened'


class DoorClosing(DoorState):
    """
    do these things when the init state is started.
    """
    
    def do_state(self, first_call):
        if first_call:
            self.logger.info("Entered state: door closing")
            # motor on
            self.RP.set_io_command('motor_reverse', 'on')
            self.start_time = time.time()
        
        # read safety switch
        self.run_time = time.time()
        if not self.RP.get_io_status("door_closed_ls"):   
           self.logger.info(f"door successfully closed after {(self.run_time - self.start_time):.2f} seconds")
           self.RP.set_io_command('motor_reverse', 'off')
           return 'DoorClosed'
        
        if not self.RP.get_io_status("safety"):    
            self.RP.set_io_command('motor_reverse', 'off')
            self.logger.warning("Through beam safety sensor triggered during door close")
            return 'DoorOpening'
        
        if (self.run_time - self.start_time) > self.DOOR_CLOSE_TIMEOUT:
            self.logger.error(f'Door closing not completed in {(self.run_time - self.start_time):.2f} seconds')
            return 'Error'
        
        if not self.RP.get_io_status("open_pb"):
            self.RP.set_io_command('motor_reverse', 'off')
            self.logger.warning("Open PB used during door close")
            return 'DoorOpening'
        
        return 'DoorClosing'
           


class Error(DoorState):
    def do_state(self, first_call):
        self.logger.error("Entered state: error")
        em.SendEmail.email_photos("Error State Entered", self.cat_name,self.log_lcn)
        self.RP.cleanup()
        sys.exit()





