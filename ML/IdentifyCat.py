import pickle
import ML.SVM_Util as SU
import os
import logging

class IDCat:
    def __init__(self,cnfg):
        self.CAT_PIX = cnfg.get_config("PHOTO_LOCATION")
        self.clf = pickle.load(open(cnfg.get_config("PICKLE_NAME"), 'rb'))
        self.CAT_NAME=cnfg.get_config("CAT_NAME")
        self.BYPASS_ID_RESULT=cnfg.get_config("BYPASS_ID_RESULT")
        self.det_path = cnfg.get_config("DETECTOR")
        self.pred_path = cnfg.get_config("PREDICTOR")
        self.logger = logging.getLogger('logger_util.email')
        self.logger.info('creating an instance of logger for email')
        self.SVM_Util = SU.SVM_Util()

    """
        A method designed to extract landmarks from a series of photos and predict whether
        or not each photo matches the specific cat that the model was trained on.
        Arguments: NA
        returns: A boolean indicating whether or not the photo is likely to be the specific
        cat the model was trained to recognize. Note that configuration information may
        override the model decision. 
    """

    def id_cat(self):
         result_list = []
         try:
             entries = os.listdir(self.CAT_PIX)
         except FileNotFoundError:
             self.logger.error(f"Error: The directory '{self.CAT_PIX}' was not found.")
         for image_file in os.listdir(self.CAT_PIX):
             landmarks = self.SVM_Util.extract_landmarks(os.path.join(self.CAT_PIX, image_file), self.pred_path, self.det_path)
             if landmarks is not None:
                  features = self.SVM_Util.normalize_landmarks(landmarks)
                  prediction = self.clf.predict([features])[0]
                  # Append a 2 to the list if the cat was identified as the one trained for
                  if prediction == 1:
                        self.logger.info(f"{image_file} identified as {self.CAT_NAME}")
                        my_cat = True
                        result_list.append(2)
                  # Append a 1 to the list if the photo contains a cat, but it's not the one trained for
                  else:
                        self.logger.info(f"{image_file} not Roscoe")
                        result_list.append(1)
             # # Append a 0 to the list if no cats were identified in the photo                        
             else:
                  self.logger.debug(f"{image_file} no landmarks extracted")       
                  result_list.append(0)    
         # for all the photos analyzed, return the result with the highest score
         return max(result_list)
               
