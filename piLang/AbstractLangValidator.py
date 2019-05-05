import abc
from piLang.piLang.Counters import Counters
from piLang.piLang.Measurement import Measurement

class AbstractLangValidator(abc.ABC):
    """
    AbstractLangValidator: Base class that any LANG validation class should implement. It provides some basic structure for a validator.
    The constructor expects a resultset dictionary and a metadata disctionary. Classes that implement this base class will have access to
    a copy of both of those objects.
    The cobstructor will also create an empty list of errors and a empty list of measurement counters.
    """

    def __init__(self:object, rs:dict, meta:dict):
        self.metaData = meta.copy()
        self.rs = rs.copy()
        self.errors = list()
        self.counters = Counters()
    
    
    def clear(self:object):
        self.errors = list()
        self.counters = Counters()
    
    
    def hasErrors(self:object) -> bool:
        # returns true if there are errors
        return ( (not self.errors is None) and (len(self.errors) > 0) )

        
    def getErrors(self:object) -> str:
        s=""
        for i in self.errors:
            s=s+i+"\n"
        return s
    
    
    @abc.abstractmethod
    def validate(self:object):
        pass

        
    @abc.abstractmethod
    def validateList(self:object, colData:dict, meta:dict):
        pass        

        
    @staticmethod
    def isBlankOrNull(value:str) -> bool:
        return ( (len(value)==0) or (value == "(Null)") )

        
    @staticmethod
    def isAllowBlank(meta:dict, value:str) -> bool:
        return ( ("AllowBlank" in meta and not meta["AllowBlank"] is None) and (meta["AllowBlank"]==True) )
     
     
    @staticmethod    
    def isFloat(value) -> bool:
        try:
            float(value)
            return True
        except Exception as e:
            return False    
    
    @staticmethod
    def isInt(value) -> bool:
        try:
            int(value)
            return True
        except Exception as e:
            return False
            