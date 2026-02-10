import cv2
import time
import os
import logging


class Cam:
    """
    An implementation of a camera class that takes
    and persists a number of photos.
    """

    def __init__(self, cnfg):
        self.logger = logging.getLogger('logger_util.camera')
        self.logger.info('creating an instance of logger for camera')
        self.dir = cnfg.get_config("PHOTO_LOCATION")
        self.num_photos = cnfg.get_config("NUM_PHOTOS")

    """ 
    A method to take photos and save to file

    """ 
    
    def take_photos(self):
      cap = cv2.VideoCapture(0)
      # Check if the camera was opened successfully
      time.sleep(2)
      if not cap.isOpened():
          self.logger.error("Error: Could not open camera.")
      else:
         # take a configurable number of photos and save to disk.  
         num_photos =0         
         while num_photos < self.num_photos:
              ret, frame = cap.read()
              if ret:
                  fname = f"{str(int(time.time()))}.jpg"
                  full_path = os.path.join(self.dir,fname)
                  cv2.imwrite(full_path, frame)
                  self.logger.info(f"Image saved as {full_path}")
                  
                  time.sleep(1)    

              else:
                  self.logger.error(f"image save failed {full_path}")
              num_photos += 1    
         # Release the camera resource
      cap.release()
      cv2.destroyAllWindows()