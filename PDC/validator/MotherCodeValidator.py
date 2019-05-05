from piLang.piLang.AbstractLangValidator import AbstractLangValidator
from piLang.piLang.Counters import Counters
from piLang.piLang.Measurement import Measurement, MeasurementCategory
from piLang.piLang.SQLTools import SQLTools


class MotherCodeValidator(AbstractLangValidator):
    """
    MotherCodeValidator: A custom validator to validate the Mother Code table as per the PDC file format spec.
    """
    
    def validate(self:object):
        self.checkMothersCode()

        
        
    def validateList(self:object, colData:dict, meta:dict):
        pass 



    def checkMothersCode(self):
        """ 
        Validates the mothers date of birth to ensure that a common data entry error (transposition) hasn't occured with other date fields. 
        """
        
        cd=dict()
        cd["Code Type"] =SQLTools.getColValues(self.rs,"Code Type")
        cd["Mothers code"] =SQLTools.getColValues(self.rs,"Mothers code")
        
        q=[dict(zip(cd, col)) for col in zip(*cd.values())]
        key="Mothers code"
        
        for i in q:
            codeType = i["Code Type"]
            code = i["Mothers code"]
                
            # todo: include ICD10 lookup validation
            if (codeType in ['T','M','P']):
                if (len(code)>5):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field mothers code with value'" + codeType + "' must be a valid 5 character ICD10 code :" + code)
            if (codeType =='O'): 
                if (len(code)>7):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field mothers code with value'" + codeType + "' must be a valid 7 character ICD10 code :" + code)                    
            elif (codeType == 'C'):
                if (code not in ['02','03','04','05','07','08','09','19','99']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field mothers code with value'" + codeType + "' must be one of [02,04,05,07,08,09,19,99]" + code)
            elif (codeType == 'L'):
                if (code not in ['02','03','04','05','10','98','99']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field mothers code with value'" + codeType + "' must be one of [02,03,04,05,06,07,10,19,99]" + code)
            elif (codeType == 'A'):
                if (code not in ['03','04','06','07','08','99']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field mothers code with value'" + codeType + "' must be one of [02,03,04,05,06,07,08,09,11,12,19,99]" + code)
            elif (codeType == 'E'):
                if (code[:2] not in ['AT','MC','PC','PO']):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: field mothers code with value'" + codeType + "' must be one of [02,03,04,05,06,07,08,10,11,12,19,99]" + code)

            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
            
    
