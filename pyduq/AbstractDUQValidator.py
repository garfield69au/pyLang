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
            raise ValidationError("LANG Exception: metadata has not been set", None)
        
        self.metadata = meta
        self.dataset = dataset
        self.counters = []
        self.data_profile = []
            
        
    def addMeasurement(self:object, measurement:Measurement):
        """
        Add a new measurement.
        """
        if (measurement is None):
            raise ValidationError("LANG Exception: Measurement has not been set", None)
        
        self.counters.append(measurement.asDict())
        
    
    def profileData(self:object, meta_attribute_definition:dict, colData:dict, key:str):
        if (colData is None):
            raise ValidationError("LANG Exception: Coldata has not been set", None)
        
        profile = DataProfile()
        profile.profileData(meta_attribute_definition, colData, key)
        profile.setPosition(len(self.data_profile)+1)
        self.data_profile.append(profile.asDict())


    def saveProfile(self:object, outputFile):
        if (len(self.data_profile)>0):
            workbook = Workbook(write_only=True)
            sheet = workbook.create_sheet()
            c=self.data_profile[0]
            headers = list(c.keys())
            sheet.append(headers)
            
            for x in self.data_profile:
                sheet.append(list(x.values()))
        
            workbook.save(filename=outputFile)
            workbook.close()


    def saveCountersSummary(self:object, outputFile):
        workbook = Workbook(write_only=True)
        sheet = workbook.create_sheet()
        headers = []
        headers.append("attribute")
        
        headers += MeasurementCategory.namesAsList()
        
        sheet.append(headers)

        summary = self.summariseCounters()
    
        for datarow in summary.values():
            for row in datarow:
                sheet.append(list(row.values()))
                
        workbook.save(filename=outputFile)
        workbook.close()


    def summariseCounters(self:object) ->dict:
        
        # get the MeasurementCategory Enum as a list
        categories = list(MeasurementCategory)
        summary = dict()
        attribute_errors = dict()
 
        # Construct a list of errors per attribute and store in a dict 
        for item in self.counters:
            key = item['attribute']
            if (not key in attribute_errors):
                attribute_errors[key] = []
            
            attribute_errors[key].append(item)
        
        # now count how many times each category appears for each attribute
        #for item, data in attribute_errors.items():
        for item in self.metadata:
            summary_row = dict()
            summary_row['attribute'] = item

            summary[item]=[]
            data = dict()
            
            if (item in attribute_errors):
                data = attribute_errors[item]
            
            for name in categories:
                error_count=0
                
                for d in data:
                    if (d['error_category'] == name.value):
                        error_count+=1
                
                # for each attribute create a list of dictionaries contaning a count of each category
                summary_row[name.name] = error_count
                        
            summary[item].append(summary_row)
                                
        return summary
        

    def saveCounters(self:object, outputFile):
        if (len(self.counters)>0):
            workbook = Workbook(write_only=True)
            sheet = workbook.create_sheet()
            headers = list(self.counters[0].keys())
            sheet.append(headers)
        
            for y in self.counters:
                sheet.append(list(y.values()))
        
            workbook.save(filename=outputFile)
            workbook.close()
    
    @abc.abstractmethod
    def validate(self:object):
        pass

        
    @abc.abstractmethod
    def validateList(self:object, key:str):
        pass        

