from piLang.piLang.Validator import Validator
from piLang.piLang.AbstractLangValidator import AbstractLangValidator
from piLang.piLang.Counters import Counters
from piLang.piLang.Measurement import Measurement, MeasurementCategory
from piLang.piLang.SQLTools import SQLTools
import datetime
import time


class MotherDetailValidator(AbstractLangValidator):
    """
    MotherDetailValidator: A custom validator to validate some of the more advanced business rules as per the PDC file format specification.
    """
    
    def validate(self:object):
        self.checkMothersDOB()
        self.checkHospitalTransferredFrom()
        self.checkTimeofTransfer()
        self.checkMotherTransferredTo()
        
        
    def validateList(self:object, colData:dict, meta:dict):
        pass 


    def checkMothersDOB(self):
        """ 
        Validates the mothers date of birth to ensure that a common data entry error (transposition) hasn't occured with other date fields. 
        """
        now = datetime.datetime.today()
        
        cd=dict()
        cd["Mothers date of birth"] =SQLTools.getColValues(self.rs,"Mothers date of birth")
        cd["Date of admission"] =SQLTools.getColValues(self.rs,"Date of admission")
        cd["Last menstrual period"] =SQLTools.getColValues(self.rs,"Last menstrual period")
        
        q=[dict(zip(cd, col)) for col in zip(*cd.values())]
        key="Mothers date of birth"
        
        for i in q:
            dob = datetime.datetime.strptime(i["Mothers date of birth"],"%Y-%m-%d %H:%M:%S")
            doa = datetime.datetime.strptime(i["Date of admission"],"%d/%m/%Y")
            if (i["Last menstrual period"] != ''):
                lmp = datetime.datetime.strptime(i["Last menstrual period"],"%d/%m/%Y")
            else:
                lmp = ''
                
            if (dob >= doa):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                self.errors.append("Error: field Mothers date of birth with value'" + i["Mothers date of birth"] + "' must be < 'Date of admission'" + i["Date of admission"])
            elif (doa.year - dob.year >60):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                self.errors.append("Error: field Mothers date of birth with value '" + i["Mothers date of birth"] + "' must be < 60 years prior to 'Date of admission'" + i["Date of admission"])
            elif (doa.year - dob.year < 10):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                self.errors.append("Error: field Mothers date of birth with value '" + i["Mothers date of birth"] + "' must be > 10 years prior to 'Date of admission'" + i["Date of admission"])
            elif (dob > now):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                self.errors.append("Error: field Mothers date of birth with value '" + i["Mothers date of birth"] + "' must be < todays date")
            elif ( (lmp != '') and (dob >= lmp) ):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                self.errors.append("Error: field Mothers date of birth with value '" + i["Mothers date of birth"] + "' must be < 'Last menstrual period'")
                
            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
            
    
    def checkHospitalTransferredFrom(self):
        """
        Validates the hospital transferred from field based on the value in the transferred antenatallly flag.
        """
    
        cd=dict()
        cd["Hospital transferred from"] =SQLTools.getColValues(self.rs,"Hospital transferred from")
        cd["Transferred antenatally flag"] =SQLTools.getColValues(self.rs,"Transferred antenatally flag")
        
        q=[dict(zip(cd, col)) for col in zip(*cd.values())]
        key="Hospital transferred from"
        
        for i in q:
        
            htf = i["Hospital transferred from"]
            ta = i["Transferred antenatally flag"]
            
            if (ta == "2" and Validator.isBlankOrNull(htf)):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                self.errors.append("Error: field 'Hospital transferred from' must not be blank if field 'Transferred antenatally flag' = 2")
            elif (ta in ["1","9"] and not Validator.isBlankOrNull(htf)):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                self.errors.append("Error: field 'Hospital transferred from' must be blank if field 'Transferred antenatally flag' = 1,9")
                
            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
            
            
    def checkTimeofTransfer(self):
        """
        Validates the time of transfer field based on the value in the transferred antenatallly flag.
        """
        
        cd=dict()
        cd["Time of transfer"] =SQLTools.getColValues(self.rs,"Time of transfer")
        cd["Transferred antenatally flag"] =SQLTools.getColValues(self.rs,"Transferred antenatally flag")
        
        q=[dict(zip(cd, col)) for col in zip(*cd.values())]
        key="Time of transfer"
        
        for i in q:
        
            tot = i["Time of transfer"]
            ta = i["Transferred antenatally flag"]
            
            if (ta == "2" and Validator.isBlankOrNull(tot)):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                self.errors.append("Error: field 'Time of transfer' must not be blank if field 'Transferred antenatally flag' = 2")
            elif (ta in ["1","9"] and not Validator.isBlankOrNull(tot)):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                self.errors.append("Error: field 'Time of transfer' must be blank if field 'Transferred antenatally flag' = 1,9")
                
            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))           

            
    def checkMotherTransferredTo(self):
        """
        Validates the hospital that the mother has been transferred to based on the value in the transferred antenatallly flag.
        """
        
        cd=dict()
        cd["Mother transferred to"] =SQLTools.getColValues(self.rs,"Mother transferred to")
        cd["Transferred antenatally flag"] =SQLTools.getColValues(self.rs,"Transferred antenatally flag")
        
        q=[dict(zip(cd, col)) for col in zip(*cd.values())]
        key="Mother transferred to"
        
        for i in q:
        
            htf = i["Mother transferred to"]
            ta = i["Transferred antenatally flag"]
            
            if (ta == "2" and Validator.isBlankOrNull(htf)):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                self.errors.append("Error: field 'Mother transferred to' must not be blank if field 'Transferred antenatally flag' = 2")
            elif (ta in ["1","9"] and not Validator.isBlankOrNull(htf)):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                self.errors.append("Error: field 'Mother transferred to' must be blank if field 'Transferred antenatally flag' = 1,9")
                
            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))           
            