import abc
from openpyxl import Workbook
from pyduq.measurement import Measurement
from pyduq.dataprofile import DataProfile
from pyduq.langerror import ValidationError
   
class AbstractDUQValidator(abc.ABC):
    """ AbstractDQValidator: 
    Base class that any data quality validation class should implement. It provides some basic structure for a validator.
    The constructor expects a resultset dictionary and a metadata disctionary. Classes that implement this base class will have access to
    a copy of both of those objects.
    The cobstructor will also create an empty list of errors and a empty list of measurement counters.
    """

    def __init__(self:object, dataset:dict, meta:dict):
        
        if (dataset is None):
            raise ValidationError("LANG Exception: DataSet has not been set", None)
        
        if (meta is None):
            raise ValidationError("LANG Exception: Metadata has not been set", None)
        
        self.metaData = meta.copy()
        self.dataset = dataset.copy()
        self.counters = list()
        self.profileList = list()
    
    
    def clear(self:object):
        self.profileList.clear()
        self.counters.clear()
        
        
    def addMeasurement(self, measurement:Measurement):
        """
        Add a new measurement.
        """
        if (measurement is None):
            raise ValidationError("LANG Exception: Measurement has not been set", None)
        
        self.counters.append(measurement.asDict())
        
    
    def profileData(self, metaAttributeDefinition:dict, colData:dict, key:str):
        if (colData is None):
            raise ValidationError("LANG Exception: Coldata has not been set", None)
        
        profile = DataProfile()
        profile.profileData(metaAttributeDefinition, colData, key)
        profile.setPosition(len(self.profileList)+1)
        self.profileList.append(profile.asDict())


    def saveProfile(self, outputFile):
        if (len(self.profileList)>0):
            workbook = Workbook()
            sheet = workbook.active
            c=self.profileList[0]
            headers = list(c.keys())
            sheet.append(headers)
        
            for x in self.profileList:
                sheet.append(list(x.values()))
        
            workbook.save(filename=outputFile)


    def saveCounters(self, outputFile):
        if (len(self.counters)>0):
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
    def validateList(self:object, colData:dict, metaAttributeDefinition:dict):
        pass        

