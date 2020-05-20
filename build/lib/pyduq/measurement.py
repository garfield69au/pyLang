import typing
from enum import Enum


class MeasurementCategory(Enum):
    """
    MeasurementCategory: An enumeration used to define which specific data quality dimension has been violated. The definition of these comes directly from LANG
    and the UQ DKE. 
    """
    
    COMPLETENESSMANDATORY = "Completeness of Mandatory Attributes"
    COMPLETENESSOPTIONAL = "Completeness of Optional Attributes"
    PRECISION = "Precision"
    BUSINESSRULECOMPLIANCE = "Business Rule Compliance"
    METADATACOMPLIANCE = "Metadata Compliance"
    UNIQUENESS = "Uniqueness"
    NONREDUNDANCY = "Non-redundancy"
    SEMANTICCONSISTENCY = "Semantic Consistency"
    VALUECONSISTENCY = "Value Consistency"
    FORMATCONSISTENCY = "Format Consistency"
	
	
    @staticmethod
    def namesAsList() ->list:
        names = []
        categories = list(MeasurementCategory)
        
        for fullname in categories:
            names.append(fullname.name)
            
        return names
        
        
class Measurement(object):
    """
    Measurement: This class is used to record an instance of a discreet measurement. Every measurement has a label, an optional errorCounter and an optional value.

    """

    def __init__(self:object, attribute:str, errorCategory:MeasurementCategory=None, description:str="<Unspecified>"):
        self.attribute = attribute
        self.errorCategory = errorCategory
        self.descr = description
    
    
    def asDict(self):
        l = dict()
        l['attribute']= self.attribute
        l['error_category'] =self.errorCategory
        l['description']=self.descr
        return l
        