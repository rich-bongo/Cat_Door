import RPi.GPIO as GPIO
import logging

class RaspPi_IO:
    
    """
    An implementation of a class that abstracts the Raspberry PI IO from business logic. Exposes a hardware  agnostic
    interface to business logic.
    """

    def __init__(self):
        self.logger = logging.getLogger('logger_util.RaspPI_IO')
        self.logger.info('creating an instance of logger')

        # map hardware input and output channels to user friendly text
        self.open_pb = 5
        self.close_pb = 6
        self.prox = 4
        self.safety = 23
        self.door_open = 27
        self.door_closed = 22
        self.motor_fwd_control = 26
        self.motor_rev_control = 20

        # configure inputs
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.open_pb, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.close_pb, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.prox, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.safety, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.door_open, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.door_closed, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # configure outputs
        GPIO.setup(self.motor_fwd_control, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.motor_rev_control, GPIO.OUT, initial=GPIO.LOW)
     

    """
        A method designed to handle output commands from business logic .
        Arguments: 
        target - the hardware items that should be modified via command
        command - the action to take on the hardware object
        returns: NA
    """ 
    def set_io_command(self, target, command):
        self.logger.info(f"output command {target}, {command}")
        if target == 'motor_forward':
            if command == 'on':
                GPIO.output(self.motor_fwd_control, True)
            if command == 'off':
                GPIO.output(self.motor_fwd_control, False)
        if target == 'motor_reverse':
            if command == 'on':
                GPIO.output(self.motor_rev_control, True)
            if command == 'off':
                GPIO.output(self.motor_rev_control, False)

    """
        A method designed to retrieve input status from the hardware 
        and return to business logic .
        Arguments: 
        target - the hardware item that is being requested
        returns: hardware input state as a boolean
    """ 

    def get_io_status(self,target):
        if target == 'open_pb':
           return GPIO.input(self.open_pb)
        if target == 'close_pb':
           return GPIO.input(self.close_pb)
        if target == 'door_open_ls':
            return GPIO.input(self.door_open)
        if target == 'door_closed_ls':
            return GPIO.input(self.door_closed)
        if target == 'prox':
            return GPIO.input(self.prox)
        if target == 'safety':
            return GPIO.input(self.safety)

    """
    A static method to clean Up IO upon termination
    """
    @staticmethod    
    def cleanup():
        GPIO.cleanup



