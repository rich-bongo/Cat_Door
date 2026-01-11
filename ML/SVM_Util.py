import cv2
import dlib
import numpy as np
 

"""
    A utility class that extracts cat faces from photos by first isolating cat faces
    from photos and then using landmarks to transform the face into a numpy array
    that can be used for binary classification. 
""" 

class SVM_Util:

    """
        A class method designed to extract landmarks .
        Arguments: 
        image_path - file locations of images
        pred_path - location of the predictor
        det_path - location of the object detector
        returns: a numpy array
    """
        
    def extract_landmarks(self,image_path, pred_path, det_path):
         self.img = cv2.imread(image_path)
         self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
         self.detector = dlib.simple_object_detector(det_path)
         self.predictor = dlib.shape_predictor(pred_path)
         self.rects = self.detector(self.gray)
         if len(self.rects) == 0:
             return None
         shape = self.predictor(self.gray, self.rects[0])
         return np.array(
             [(shape.part(i).x, shape.part(i).y) for i in range(shape.num_parts)])
    
    """
        A class method designed to normalize landmarks.
        Arguments: 
        lm  - landmarks as a numpy array
        returns - normalized landmarks as a numpy array
    """
     
    def normalize_landmarks(self,lm):
         # Convert to numpy array
         points = np.array(lm)
         # Center and scale
         centered = points - np.mean(points, axis=0)
         scale = np.linalg.norm(centered)
         return (centered / scale).flatten()