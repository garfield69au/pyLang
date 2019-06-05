from enum import Enum
import re
import time
from prettytable import PrettyTable
from piLang.piLang.Validator import Validator
from piLang.piLang.AbstractLangValidator import AbstractLangValidator
from piLang.piLang.LangError import ValidationError
from piLang.piLang.Measurement import Measurement, MeasurementCategory
from piLang.piLang.Counters import Counters
from piLang.piLang.ExpressionBuilder import ExpressionBuilder
from piLang.piLang.SQLTools import SQLTools


class PatternFormat(Enum):
    # an enumartion of various data patterns that cen be used for regex parsing
    DATE_YYMMDD = "^(((0[1-9]|[12][0-9]|30)[-/]?(0[13-9]|1[012])|31[-/]?(0[13578]|1[02])|(0[1-9]|1[0-9]|2[0-8])[-/]?02)[-/]?[0-9]{4}|29[-/]?02[-/]?([0-9]{2}(([2468][048]|[02468][48])|[13579][26])|([13579][26]|[02468][048]|0[0-9]|1[0-6])00))$"
    TIME_HHMM = "([01]?[0-9]|2[0-3])[0-5][0-9]"
    DATE_DD = "[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) (2[0-3]|[0-1][0-9]):[0-5][0-9]"

    
class LangValidator(AbstractLangValidator):
    """
    LangValidator: A generic validator for LANG. 
    The main execution method is validate().
    """   
        
    def validate(self:object):
        """
        Iterate through each column of the metadata, and execute a series of validations against each column in the resultset.
        Any errors found are added to self.errors, and a count for each validation and error is maintained in self.counters
        """
        self.clear()
        
        if (self.metaData is None):
            raise ValidationError("LANG Exception: meta data has not been set", None)
        elif (self.rs is None):
            raise ValidationError("LANG Exception: resultset has not been set", None)
        
        for col in self.metaData:
            colData = SQLTools.getCol(self.rs, col)
            if ( (not colData is None) and (len(colData[col]) > 0) ):
                self.validateList(colData, self.metaData[col])
                #raise ValidationError("LANG Exception: Could not locate column '" + col + "' in resultset", None)
            else:
                #if (len(self.metaData[col]) != len(colData)):
                self.counters.add(Measurement(col,attributeCount=1,errorCount=1,errorCategory=MeasurementCategory.CONFORMANCE.value))
                self.errors.append("Error: Could not locate column '" + col + "' in row")
                
            
    def validateList(self:object, colData:dict, meta:dict):

        """
        Execute a series of validations against the supplied column of data and the metadata for the column.
        Which validation is run is determined by entries in the metadata.
        """        
        # As there is only one row in the dictionay, obtain that row
        key = next(iter(colData))
        row = colData[key]          
        
        for value in row:
            self.checkMandatory(meta, key, value)                  
            self.checkSize(meta, key, value)
            self.checkType(meta, key, value)
            self.checkEnum(meta, key, value)
            self.checkStartsWith(meta, key, value)
            self.checkFormat(meta, key, value)                        
            self.checkUnique(meta, row, key, value)

        self.checkComposite(meta, key)            
        # expression evaluation is different to processing field specific validations as it could link in other columns from the resultset
        self.evaluateExpression(meta, key)
        
        
    def checkMandatory(self, meta:dict, key:str, value:str):
        # mandatory field check
        if (Validator.exists(meta, "Mandatory") and (Validator.isTrue(meta, "Mandatory")) ):
            if ( (Validator.isBlankOrNull(value)) and (not Validator.isAllowBlank(meta)) ):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.MANDATORYCOMPLETENESS.value))
                self.errors.append("Error: Mandatory field '" + key + "' is BLANK or NULL. A value is required.")
                
            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.MANDATORYCOMPLETENESS.value))
             
        else:
            # optional field check. According to LANG optional fields shpuld contain some sort of default value
            # i.e. no field shpould ever be blank or NULL.
            if ( (Validator.isBlankOrNull(value)) and (not Validator.isAllowBlank(meta)) ):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.OPTIONALCOMPLETENESS.value))
                self.errors.append("Error: Optional field '" + key + "' is BLANK or NULL. A default value is required.")
            # turned off to reduce the amount of noise on the output
            #else:
            #    print("Warning: Field '" + key + "' is blank and should have a default value.")
                    
            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.OPTIONALCOMPLETENESS.value))

            
    def checkComposite(self, meta:dict, key:str):
        # unique field check
        if (Validator.exists(meta, "Composite")):
            # sum the number of times value appears in the row. this is faster than using list.count(value)
            listOfKeys = meta["Composite"]
            # Concatenate the list of keys into a composite key string
            keyStr = '+'.join(map(str, listOfKeys))
            keyStr = keyStr.replace("%1", key)
        
            # populate a dictionary of just the values that are required to create the composite key
            keyData=dict()
            for col in listOfKeys:
                col = col.replace("%1", key)
                keyData[col]=SQLTools.getColValues(self.rs, col)
            
            seen=list()
            rowindex=0
            # convert the dictionary of columns into a list of tuples
            fields=[dict(zip(keyData, col)) for col in zip(*keyData.values())]
            
            # check to see if there is are any duplicates in the order of keys provided
            for row in fields:
                # join the values from the columns that make up the composite key to form a single value
                s = ''.join(map(str, row.values()))
                if (s in seen):
                    self.counters.add(Measurement(keyStr,errorCount=1,errorCategory=MeasurementCategory.UNIQUENESSCOMPOSITE.value))
                    self.errors.append("Error: Duplicate composite key: '" + keyStr + "', value: '" + s + "'")
                else:
                    seen.append(s)
                
                self.counters.add(Measurement(keyStr,attributeCount=1,errorCategory=MeasurementCategory.UNIQUENESSCOMPOSITE.value))

                        
    def checkSize(self, meta:dict, key:str, value:str):
        # field length check
        if (Validator.exists(meta, "Size")):
            if ( (len(value) > int(meta["Size"])) and (not Validator.isBlankOrNull(value)) ):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.METACOMPLIANCESIZE.value))
                self.errors.append("Error: Field '" + key + "' with value '" + value + "' is longer than size '" + str(meta["Size"]) + "'")
                
            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.METACOMPLIANCESIZE.value))

            
    def checkType(self, meta:dict, key:str, value:str):
        # field type check
        isValidType = False
        
        if (Validator.exists(meta, "Type")):
            if (meta["Type"]=="int"):
                if ( (Validator.isBlankOrNull(value)) or (not Validator.isInt(value)) ):
                    if (not Validator.isAllowBlank(meta)):
                        self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.METACOMPLIANCETYPE.value))
                        self.errors.append("Error: Field '" + key + "' with value '" + value + "' is not an int")
                else:
                    isValidType = True
                    
            elif (meta["Type"]=="float"):
                if ( (Validator.isBlankOrNull(value)) or (not Validator.isFloat(value)) ): 
                    if (not Validator.isAllowBlank(meta, value)):
                        self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.METACOMPLIANCETYPE.value))
                        self.errors.append("Error: Field '" + key + "' with value '" + value + "' is not a float")
                else:
                    isValidType = True
                
            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.METACOMPLIANCETYPE.value))

        # given that min and max checks only apply to int and float values we may as well test for them now
        if (isValidType):
            self.checkMinMax(meta, key, value)
            

    def checkMinMax(self, meta:dict, key:str, value:str):
        # field value range check (int and float only although in theory we could specify min and max ranges for other attributes)
        min = -1
        max = -1
        
        if (Validator.exists(meta, "Min")):
            try:
                min = float(meta["Min"])
            except Exception as e:
                pass
        
        if (Validator.exists(meta, "Max")):
            try:
                max = float(meta["Max"])
            except Exception as e:
                pass

        if (min != -1):
            if (float(value) < min):
                # error
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.METACOMPLIANCERANGEMIN.value))
                self.errors.append("Error: Field '" + key + "' with value '" + value + "' must be >= " + str(min))
            
            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.METACOMPLIANCERANGEMIN.value))
                
        if (max != -1):
            if (float(value) > max):
                # error
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.METACOMPLIANCERANGEMAX.value))
                self.errors.append("Error: Field '" + key + "' with value '" + value + "' must be <= " + str(max))
            
            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.METACOMPLIANCERANGEMAX.value))


    def checkEnum(self, meta:dict, key:str, value:str):
        # enumerated field check
        if (Validator.exists(meta, "Enum")):
            # enum is expected to be a list
            enum = meta["Enum"]
            
            # check that the value exists within the provided list. If the value is blank then ignore it 
            # as we should have picked it up in the mandatory/optional test anyway
            # (i.e. if the field is optional but a value has been provided then we check it against the supplied list)
            if ( (len(value)>0) and (value not in enum) and (value != "(Null)") ):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.METACOMPLIANCEENUM.value))
                self.errors.append("Error: Field '" + key + "' with value '" + value + "' is outside the range of: " + str(enum))

            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.METACOMPLIANCEENUM.value))


    def checkStartsWith(self, meta:dict, key:str, value:str):
        # enumerated field check
        if (Validator.exists(meta, "StartsWith")):
            # startsWith is expected to be a list
            startsWith = meta["StartsWith"]
            
            # check that the value exists within the provided list. If the value is blank then ignore it 
            # as we should have picked it up in the mandatory/optional test anyway
            # (i.e. if the field is optional but a value has been provided then we check it against the supplied list)
            if ( (len(value)>0) and (value != "(Null)") ):
                found = False
                for s in startsWith:
                    if value.startswith(s):
                        found = True
                        break
                        
                if (not found):
                    self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.FORMATCONSISTENCYPREFIX.value))
                    self.errors.append("Error: Field '" + key + "' with value '" + value + "' does not begin with any of: " + str(startsWith))

            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.FORMATCONSISTENCYPREFIX.value))

            
    def checkFormat(self, meta:dict, key:str, value:str):
        # format check (must provide a regex)
        if (Validator.exists(meta, "Format")):
            re.purge()
            isMatch = (not re.match(meta["Format"], value) is None)
            if ( (not isMatch) and (not Validator.isAllowBlank(meta)) ):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.FORMATCONSISTENCY.value))
                self.errors.append("Error: Field '" + key + "' with value '" + value + "' does not match regex '" + meta["Format"] + "'")
            
            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.FORMATCONSISTENCY.value))

            
    def checkUnique(self, meta:dict, row:list, key:str, value:str):
        # unique field check
        if (Validator.exists(meta, "Unique") and (Validator.isTrue(meta, "Unique")) ):
            # sum the number of times value appears in the row. this is faster than using list.count(value)
            counter = sum(1 for i in row if str(i) == value)
            
            # create a list with every entry of value in the row. If there are duplicates then the resulting list will have >1 entries
            if (counter>1):
                self.counters.add(Measurement(key,errorCount=1,errorCategory=MeasurementCategory.UNIQUENESS.value))
                self.errors.append("Error: Field '" + key + "' with value '" + value + "' is not UNIQUE")

            self.counters.add(Measurement(key,attributeCount=1,errorCategory=MeasurementCategory.UNIQUENESS.value))

            
    def evaluateExpression(self, meta:dict, key:str):
        # evaluate any custom expressions
        if (Validator.exists(meta, "Expression")):
            expr = meta["Expression"]
            
            # %1 is a placeholder for whatever the column name is owning the expression (it's just a shortcut)
            expr = expr.replace("%1", "[" + key + "]")
            exp = ExpressionBuilder()
            
            fields = exp.parseExpr(expr)
            cd = dict()
            
            # grab all of the columns that we need and store in a local dict
            for f in fields:
                
                # grab the column data out of the resultset
                colData = SQLTools.getCol(self.rs, f)
                
                # if the column couldn't be found then we have a configuration issue so raise an exception
                if (colData is None):
                    raise ValidationError("Error evaluating expression: '" + expr + "'. Unable to find column '" + f + "' in the resultset", None)
                
                cd.update(colData)
            
            # convert the seperate columns into rows of tuples
            q=[dict(zip(cd, col)) for col in zip(*cd.values())]
            
            for i in q:
                result=None
                ev = exp.merge(expr,i)
                
                try:
                    result = eval(ev)
                except Exception as e:
                    print("Warning: An error occured while evaluating expression: '" + ev + "': " + str(e))
                    
                    self.counters.add(Measurement(expr,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: Expression '" + ev + "' returned an error '" + str(e) + "'")

                if ( (not result is None) and (result == False) ):
                    self.counters.add(Measurement(expr,errorCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
                    self.errors.append("Error: Expression '" + ev + "' returned FALSE")

                self.counters.add(Measurement(expr,attributeCount=1,errorCategory=MeasurementCategory.RULECOMPLIANCE.value))
    
