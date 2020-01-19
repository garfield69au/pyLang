import typing
from piLang.piLang.Measurement import Measurement
from prettytable import PrettyTable

class Counters(object):
    """
    Counters: This is a dictionary class that encapsulates Measurement objects.
    The class will ensure that only 1 instance of a named measurement object
    exists in the dict, and will append errors to a list per attribute.
  
    """
    
    def __init__(self, *args, **kwargs): 
        self.counters = list()
    
    
    def add(self, measurement:Measurement):
        """
        Add a new measurement.
        """      
        
        self.counters.append(measurement.asDict())
        
