from sklearn.svm import SVC
import os
import pickle
#import SVM_Util as SU

from sklearn.decomposition import PCA as RandomizedPCA
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
import json
import sys

#sys.path.append('/home/richj/Cat_Door')
print(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import ML.SVM_Util as SU

"""
read photo files for target and non-target cat.
use SVM_Util to extract landmarks from photos and normalize resulting arrays
create train and test arrays of labeled data
feed arrays to SVC and fit to data.
save resulting model using pickle
"""

X = []
y = []
SVM_Util = SU.SVM_Util()
TARGET_CAT_TRAINING_DIR = ""
NON_TARGET_CAT_TRAINING_DIR = ""
pred_path = ""
det_path = ""
fldr_out = ""

landmark_found = 0
landmark_not_found = 0



def load_config():
    global TARGET_CAT_TRAINING_DIR
    global NON_TARGET_CAT_TRAINING_DIR
    global pred_path
    global det_path
    global fldr_out

    full_path = 'Training/config_data.json'
    try:
        with open(full_path, 'r') as f:
            config_data = json.load(f)
            try:
                TARGET_CAT_TRAINING_DIR = config_data["Target"]
                NON_TARGET_CAT_TRAINING_DIR = config_data["Non_Target"]
                pred_path = config_data["pred"]
                det_path = config_data["det"]
                fldr_out = config_data['write_to']
            except KeyError:
                print(" Key not found... Terminating ")
                sys.exit()

    except FileNotFoundError:
        print(f"configuration file: {full_path} not found..."
              "terminating")
        sys.exit()

    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {full_path}... terminating")
        sys.exit()


def train_cat(fldr, lbl):
    global landmark_found
    global landmark_not_found
    for image_file in os.listdir(fldr):
        landmarks = SVM_Util.extract_landmarks(os.path.join(fldr,image_file),pred_path, det_path)
        
        if landmarks is not None:
            print(f"landmarks found for {image_file}")
            features = SVM_Util.normalize_landmarks(landmarks)            
            X.append(features)
            y.append(lbl)
            landmark_found += 1
        else:
            print(f"landmarks NOT found for {image_file}")
            landmark_not_found += 1


load_config()
train_cat(TARGET_CAT_TRAINING_DIR, 1)
train_cat(NON_TARGET_CAT_TRAINING_DIR, 0)

# X = list of normalized landmark vectors
# y = list of labels: 1 for your cat, 0 for others
pca = RandomizedPCA(n_components=16, whiten=True, random_state=42)
svc = SVC(kernel='rbf', class_weight='balanced')
clf = make_pipeline(pca, svc)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25,random_state=42)
clf.fit(X, y)  # X = features, y = [1, 0, 0, 1, ...]
accuracy = clf.score(X_test, y_test)
print(f"accuracy:{accuracy}, photos with landmarks Found:{landmark_found}, "
      f" photos with Landmarks not found {landmark_not_found} ")

# Save the trained model
filename = os.path.join(fldr_out,'svc_model.pkl')
pickle.dump(clf, open(filename, 'wb'))
