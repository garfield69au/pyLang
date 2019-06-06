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

    Example use:
    m = Measurement("Frog")
    m = Measurement("Frog",errorCount=1000)
    """

    def __str__(self:object):
        return self.__repr__()
    
    def __repr__(self:object):
        return "[Measurement: {0}\terrorCount: {1}\tattributeCount: {2}\tMean: {3}\terrorCategory: {4}]\n".format(self.attribute,self.errorCount,self.attributeCount,self.mean, self.errorCategory)

    def __init__(self:object, attribute:str, attributeCount:int=0, errorCount:int=0, errorCategory:MeasurementCategory=None):
        self.attribute = attribute
        self.attributeCount = attributeCount
        self.errorCount = errorCount
        self.errorCategory = errorCategory
        self.mean = -1.0
        self.percent=-1.0
        
    def calcMean(self):
        try:
            # prevent divide by zero errors
            self.mean = round (self.attributeCount / self.errorCount, 2)
            return self.mean
        except Exception as e:
            return -1.0

    def calcPercent(self):
        try:
            # prevent divide by zero errors
            self.percent = round(self.errorCount / self.attributeCount *100.0, 2)
            return self.percent
        except Exception as e:
            return -1.0
        
    def values(self):
        l = list()
        l.append(self.attribute)
        l.append(self.attributeCount)
        l.append(self.errorCategory)
        l.append(self.errorCount)
        l.append(self.mean)
        l.append(self.percent)
        return l
    
    def keys(self):
        l = list()
        l.append('attribute')
        l.append('attributeCount')
        l.append('errorCategory')
        l.append('errorCount')
        l.append('Mean')
        l.append('Percent')
        return l
    
    def asDict(self):
        l = dict()
        l['attribute']= self.attribute
        l['attributeCount'] = self.attributeCount
        l['errorCategory'] =self.errorCategory
        l['errorCount']= self.errorCount
        l['Mean']= self.mean
        l['Percent'] = self.percent
        return l
        
