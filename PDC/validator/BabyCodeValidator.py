from piLang.piLang.AbstractLangValidator import AbstractLangValidator
from piLang.piLang.Counters import Counters
from piLang.piLang.Measurement import Measurement, MeasurementCategory
from piLang.piLang.SQLTools import SQLTools


class BabyCodeValidator(AbstractLangValidator):
    """
    BabyCodeValidator: A custom validator to validate the Baby Code table as per the PDC file format spec.
    """
    
    def validate(self:object):
        self.checkBabyCode()

        
        
    def validateList(self:object, colData:dict, meta:dict):
        pass 



    def checkBabyCode(self):
        """ 
        Validates the mothers date of birth to ensure that a common data entry error (transposition) hasn't occured with other date fields. 
        """
        
        cd=dict()
        cd["Code Type"] =SQLTools.getColValues(self.rs,"Code Type")
        cd["Babys birth code"] =SQLTools.getColValues(self.rs,"Babys birth code")
        
        q=[dict(zip(cd, col)) for col in zip(*cd.values())]
        key="Babys birth code"
        
        for i in q:
            codeType = i["Code Type"]
            code = i["Babys birth code"]
                
            # todo: include ICD10 lookup validation
            if (codeType in ['L','P','M']):
                if (len(code)>5):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field baby code with value'" + codeType + "' must be a valid ICD10 code :" + code)
            elif (codeType == 'C'):
                if (len(code)>5):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field baby code with value'" + codeType + "' must be a valid ICD10 code :" + code)
            elif (codeType == 'I'):
                if (code not in ['1','2','3','6','7','8','9']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field baby code with value'" + codeType + "' must be one of [1,2,3,6,7,8,9]" + code)
            elif (codeType == 'A'):
                if (code not in ['02','04','05','07','08','10','19','99']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field baby code with value'" + codeType + "' must be one of [02,04,05,07,08,10,19,99]" + code)
            elif (codeType == 'S'):
                if (code not in ['02','03','04','05','06','07','10','19','99']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field baby code with value'" + codeType + "' must be one of [02,03,04,05,06,07,10,19,99]" + code)
            elif (codeType == 'R'):
                if (code not in ['02','03','04','05','06','07','08','09','11','12','19','99']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field baby code with value'" + codeType + "' must be one of [02,03,04,05,06,07,08,09,11,12,19,99]" + code)
            elif (codeType == 'T'):
                if (code not in ['02','03','04','05','06','07','08','10','11','12','19','99']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field baby code with value'" + codeType + "' must be one of [02,03,04,05,06,07,08,10,11,12,19,99]" + code)
            elif (codeType == 'N'):
                if (code not in ['02','03','04','05','06','07','08','09','10','11','98','99']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field baby code with value'" + codeType + "' must be one of [02,03,04,05,06,07,08,09,10,11,98,99]" + code)
            elif (codeType == 'F'):
                if (code not in ['1','2','3','4','9']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field baby code with value'" + codeType + "' must be one of [1,2,3,4,9]" + code)
            elif (codeType == 'D'):
                if (code not in ['1','2','3','4','9']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field baby code with value'" + codeType + "' must be one of [1,2,3,4,9]" + code)
            elif (codeType == 'E'):
                if (code[:2] not in ['IM','IO','IT','FV','CM','CO','CT','LD','PU','NM','CA','RN']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field baby code with value'" + codeType + "' must be one of [IM,IO,IT,FV,CM,CO,CT,LD,PU,NM,CA,RN]" + code)
            elif (codeType == 'B'):
                if (code not in ['02','03','04','98','99']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field baby code with value'" + codeType + "' must be one of [02,03,04,98,99]" + code)
            elif (codeType == 'G'):
                if (code not in ['2','3','4','8','9']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field baby code with value'" + codeType + "' must be one of [2,3,4,8,9]" + code)
            elif (codeType == 'V'):
                if (code not in ['02','03','04','05','06','98','99']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field baby code with value'" + codeType + "' must be one of [02,03,04,05,06.98,99]" + code)
                    
            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
            
    
