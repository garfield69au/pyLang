import typing
from enum import Enum


class DataQualityDimension(Enum):
    """ MeasurementCategory: An enumeration used to define which specific data quality dimension has been violated. The definition of these comes directly from LANG
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
    def names() ->list:
        names = []
        for fullname in list(DataQualityDimension):
            names.append(fullname.name)
        return (names)
        
        
class DataQualityError(object):
    """ Measurement: This class is used to record an instance of a discreet measurement. Every measurement has a label, an optional errorCounter and an optional value.
    """

    def __init__(self:object, attribute:str, error_dimension:DataQualityDimension=None, description:str="<Unspecified>"):
        self.attribute = attribute
        self.error_dimension = error_dimension
        self.error_descr = description
    
    
    def to_dict(self):
        values = {}
        values['attribute']= self.attribute
        values['error_dimension'] =self.error_dimension
        values['description']=self.error_descr
        return values
        