import typing
from piLang.piLang.Measurement import Measurement
from prettytable import PrettyTable

class Counters(dict):
    """
    Counters: This is a dictionary class that encapsulates Measurement objects.
    The class will ensure that only 1 instance of a named measurement object
    exists in the dict.
    The class also provides a couple of helper functions to increment or
    decrement specific measurement counters.
    """
    def __str__(self):
        return self.__repr__()

    def __repr__(self):   
        pt = PrettyTable()
        if (len(self)>0):
            c=next(iter(self.values()))
            pt.field_names = c.keys()
            
            x=list()
            s=""
            for i in self:
                pt.add_row([f for f in self[i].values()])
                #print(self[i].item)
                '''
                if (s == ""):
                    s = self[i].item
                    x.clear()
                    x.append(self[i].values())
                elif (s == self[i].item):
                    x.append(self[i].values())
                else:
                    s = self[i].item
                    #pt.add_row([f for f in x])
                    print(x)
                    x.clear()
                    x.append(self[i].values())
            
            #print(x)
                '''            
        return str(pt)
        
    def __init__(self, *args, **kwargs): 
        dict.__init__(self, *args, **kwargs) 
        
    
    def add(self, measurement:Measurement):
        """
        Add a new measurement.
        If the named measurement doesn't exist, then create a new entry.
        If the named entry does exist, then increment its counter.
        This side-effect is designed to simplify programming (i.e.
        prevents the need of having to first test to see if a measurement exists)
        """      
        key = measurement.attribute + ":" + measurement.errorCategory
        
        # first we check to ensure the item we are adding doesn't already exist
        if (key not in self):
            # add the new measurement
            self[key]=measurement
        else:
            # if we already have this measurement item then just accumulate the values (i.e. perform an update)
            self[key].attributeCount += measurement.attributeCount
            self[key].errorCount += measurement.errorCount
        
    def calcMean(self):
        for item in self:
            self[item].calcMean()
            
    def calcPercent(self):
        for item in self:
            self[item].calcPercent()            
    
    def max(self):
        return len(self)
    

    def toList(self):
        """
        Returns this dictionary as a list of dictionary objects (each Measurement is serialised into its own dict.
        """
        l=list()
    
        for index in self:
            l.append(self[index].asDict())
            
        return l
