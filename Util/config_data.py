import json
import sys
import os
import logging

"""
    A class that reads an application common configuration file and
    exposes an interface for classes to retrieve configuration data.  
"""

class ConfigUtility:
    
    def __init__(self):
        self.logger = logging.getLogger('logger_util.config')
        self.logger.info('creating an instance of logger for config')
    
    
    """
    Terminate application if requested configuration data not found
    """
    def needed_config_value_not_found(self,item):
        self.logger.info(f"A required configuration item was not found {item}.. Terminating script")
        sys.exit()

    """
        A method to load the configuration json file and save as a dictionary
        Arguments: NA
        returns: NA
    """
    def load_config(self):
        path = 'config'
        fname = 'config_data.json'
        full_path = os.path.join(path, fname)
        try:
            with open(full_path, 'r') as f:
                config_data = json.load(f)
                return config_data
        except FileNotFoundError:
            print("configuration file: config\\config_data.json not found..."
                  "terminating")
            sys.exit()

        except json.JSONDecodeError:
            self.logger.error(f"Error: Could not decode JSON from {path}")
            return None

    """
        A method to return configuration values
        Arguments: Requested Configuration Name
        returns: Configuration value
    """
    def get_config(self,cfg_name):
        config_data = self.load_config()
        try:
            return config_data[cfg_name]
        except KeyError:
            self.needed_config_value_not_found(cfg_name)
            #self.logger.error(f"value for key {cfg_name} not found.... skipping")
            #return "KEY NOT FOUND"


     

