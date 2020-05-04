import abc
from openpyxl import Workbook
from pyduq.measurement import Measurement, MeasurementCategory
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


    def saveCountersSummary(self, outputFile):
        workbook = Workbook()
        sheet = workbook.active
        headers = list()
        headers.append("attribute")
        
        headers += MeasurementCategory.namesAsList()
        
        sheet.append(headers)

        summary = self.summariseCounters()
    
        for datarow in summary.values():
            for row in datarow:
                sheet.append(list(row.values()))
        
        
        workbook.save(filename=outputFile)


    def summariseCounters(self) ->dict:
        
        # get the MeasurementCategory Enum as a list
        categories = list(MeasurementCategory)
        summary = dict()
        attributeErrors = dict()
 
        # Construct a list of errors per attribute and store in a dict 
        for item in self.counters:
            key = item['attribute']
            if (not key in attributeErrors):
                attributeErrors[key] = list()
            
            attributeErrors[key].append(item)
        
        # now count how many times each category appears for each attribute
        #for item, data in attributeErrors.items():
        for item in self.metaData:
            summaryRow = dict()
            summaryRow['attribute'] = item

            summary[item]=list()
            data = dict()
            
            if (item in attributeErrors):
                data = attributeErrors[item]
            
            for name in categories:
                errorCount=0
                
                for d in data:
                    if (d['error_category'] == name.value):
                        errorCount+=1
                
                # for each attribute create a list of dictionaries contaning a count of each category
                summaryRow[name.name] = errorCount
                        
            summary[item].append(summaryRow)
                                
        return summary
        

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

