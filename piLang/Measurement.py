import typing
from enum import Enum


class MeasurementCategory(Enum):
    """
    MeasurementCategory: An enumeration used to define which specific data quality dimension has been violated. The definition of these comes directly from LANG
    and the UQ DKE. 
    """
    
    UNIQUENESS = "Uniqueness"
    UNIQUENESSCOMPOSITE = "Uniqueness (composite key)"
    FORMATCONSISTENCY = "Format Consistency"
    FORMATCONSISTENCYPREFIX = "Format Consistency (starts with)"
    VALUECONSISTENCY = "Value Consistency"
    METACOMPLIANCESIZE = "Meta Compliance (field size)"
    METACOMPLIANCETYPE = "Meta Compliance (data type)"
    METACOMPLIANCERANGEMIN = "Meta Compliance (min value)"
    METACOMPLIANCERANGEMAX = "Meta Compliance (max value)"
    METACOMPLIANCEENUM = "Meta Compliance (enumeration)"
    RULECOMPLIANCE = "Business Rule Compliance"
    MANDATORYCOMPLETENESS = "Completeness of Mandatory fields"
    OPTIONALCOMPLETENESS = "Completeness of Optional fields"
    AVAILABILITY = "Availability & Accessibility"
    CONFORMANCE = "Conformance to meta data (missing column)"
    
    
class Measurement(object):
    """
    Measurement: This class is used to record an instance of a discreet measurement. Every measurement has a label, an optional errorCounter and an optional value.

    """

    def __init__(self:object, attribute:str, errorCategory:MeasurementCategory=None, description:str="<Unspecified>"):
        self.attribute = attribute
        self.errorCategory = errorCategory
        self.descr = description

    """
    def calcMean(self):
        try:
            # prevent divide by zero errors
            
            if (self.errorCount > 0):
                self.mean = round (self.attributeCount / self.errorCount, 4)
            
            if (self.errorCount == 0 and self.attributeCount > 0):
                self.confidenceScore = 1.0
            else:
                self.confidenceScore = round (1.0 - (self.errorCount / self.attributeCount), 4)
            
            return self.mean
        except Exception as e:
            return -1.0
    """
    
        
    def values(self):
        l = list()
        l.append(self.attribute)
        l.append(self.errorCategory)
        l.append(self.descr)
        return l
 
    @staticmethod 
    def keys():
        l = list()
        l.append('attribute')
        l.append('error_category')
        l.append('description')
        return l
    
    def asDict(self):
        l = dict()
        l['attribute']= self.attribute
        l['error_category'] =self.errorCategory
        l['description']=self.descr
        return l
        