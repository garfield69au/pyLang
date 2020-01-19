import abc
from enum import Enum
from piLang.piLang.Counters import Counters
from piLang.piLang.Measurement import Measurement
from piLang.piLang.Profile import Profile
from openpyxl import Workbook

class PatternFormat(Enum):
    # an enumartion of various data patterns that cen be used for regex parsing
    DATE_YYMMDD = "^(((0[1-9]|[12][0-9]|30)[-/]?(0[13-9]|1[012])|31[-/]?(0[13578]|1[02])|(0[1-9]|1[0-9]|2[0-8])[-/]?02)[-/]?[0-9]{4}|29[-/]?02[-/]?([0-9]{2}(([2468][048]|[02468][48])|[13579][26])|([13579][26]|[02468][048]|0[0-9]|1[0-6])00))$"
    TIME_HHMM = "([01]?[0-9]|2[0-3])[0-5][0-9]"
    DATE_DD = "[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) (2[0-3]|[0-1][0-9]):[0-5][0-9]"
    DATE_DDMMYYYY = r"^(?=\d{2}([-.,\/])\d{2}\1\d{4}$)(?:0[1-9]|1\d|[2][0-8]|29(?!.02.(?!(?!(?:[02468][1-35-79]|[13579][0-13-57-9])00)\d{2}(?:[02468][048]|[13579][26])))|30(?!.02)|31(?=.(?:0[13578]|10|12))).(?:0[1-9]|1[012]).\d{4}$"
    PHONE = r"^(\+1|1)?[2-9]\d\d[2-9]\d{6}$"

   
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
        self.counters = Counters()
        self.profileList = list()
    
    
    def clear(self:object):
        self.profileList.clear()
    
    def profileData(self, meta:dict, col:dict, key:str):
        profile = Profile()
        profile.profileData(meta, col, key)
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
        headers = list(self.counters.counters[0].keys())
        sheet.append(headers)
        
        for y in self.counters.counters:
            sheet.append(list(y.values()))
        
        workbook.save(filename=outputFile)
    
    
    @abc.abstractmethod
    def validate(self:object):
        pass

        
    @abc.abstractmethod
    def validateList(self:object, colData:dict, meta:dict):
        pass        

        