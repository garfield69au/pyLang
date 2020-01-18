import typing
from piLang.piLang.Measurement import Measurement
from prettytable import PrettyTable

class Counters(dict):
    """
    Counters: This is a dictionary class that encapsulates Measurement objects.
    The class will ensure that only 1 instance of a named measurement object
    exists in the dict, and will append errors to a list per attribute.
  
    """
    
    def __init__(self, *args, **kwargs): 
        dict.__init__(self, *args, **kwargs) 
        
    
    def add(self, measurement:Measurement):
        """
        Add a new measurement.
        """      
        key = measurement.attribute

        if not (key in self.keys()):
            self[key] = list()
            
        self[key].append(measurement)
        
      
    def max(self):
        return len(self)
    

    def toList(self):
        """
        Returns this dictionary as a list of dictionary objects (each Measurement is serialised into its own dict.
        """
        return [self[index] for index in self]
        
