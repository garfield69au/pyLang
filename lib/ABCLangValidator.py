import abc
from pyLang.lib.measurement import Measurement
from pyLang.lib.dataprofile import DataProfile
from openpyxl import Workbook

   
class ABCLangValidator(abc.ABC):
    """ ABCLangValidator: 
    Base class that any LANG validation class should implement. It provides some basic structure for a validator.
    The constructor expects a resultset dictionary and a metadata disctionary. Classes that implement this base class will have access to
    a copy of both of those objects.
    The cobstructor will also create an empty list of errors and a empty list of measurement counters.
    """

    def __init__(self:object, rs:dict, meta:dict):
        self.metaData = meta.copy()
        self.rs = rs.copy()
        self.counters = list()
        self.profileList = list()
    
    
    def clear(self:object):
        self.profileList.clear()
        self.counters.clear()
        
        
    def addMeasurement(self, measurement:Measurement):
        """
        Add a new measurement.
        """      
        self.counters.append(measurement.asDict())
        

    
    def profileData(self, meta:dict, col:dict, key:str):
        profile = DataProfile()
        profile.profileData(meta, col, key)
        profile.setPosition(len(self.profileList)+1)
        self.profileList.append(profile.asDict())


    def saveProfile(self, outputFile):
        workbook = Workbook()
        sheet = workbook.active
        c=self.profileList[0]
        headers = list(c.keys())
        sheet.append(headers)
        
        for x in self.profileList:
            sheet.append(list(x.values()))
        
        workbook.save(filename=outputFile)


    def saveCounters(self, outputFile):
        workbook = Workbook()
        sheet = workbook.active
        headers = list(self.counters[0].keys())
        sheet.append(headers)
        
        for y in self.counters:
            sheet.append(list(y.values()))
        
        workbook.save(filename=outputFile)
    
    
    @abc.abstractmethod
    def validate(self:object):
        pass

        
    @abc.abstractmethod
    def validateList(self:object, colData:dict, meta:dict):
        pass        

