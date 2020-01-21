import re
import time
from piLang.piLang.Validator import Validator
from piLang.piLang.AbstractLangValidator import AbstractLangValidator
from piLang.piLang.LangError import ValidationError
from piLang.piLang.Measurement import Measurement, MeasurementCategory
from piLang.piLang.ExpressionBuilder import ExpressionBuilder
from piLang.piLang.SQLTools import SQLTools
from piLang.piLang.Profile import Profile

 
class LangValidator(AbstractLangValidator):
    """
    LangValidator: A generic validator for LANG. 
    The main execution method is validate().
    """   
        
    def validate(self:object):
        """
        Validate a resultset against predefined metadata based on the LANG rules of data quality.
        """
        self.clear()

        
        if (self.metaData is None):
            raise ValidationError("LANG Exception: meta-data has not been set", None)
        elif (self.rs is None):
            raise ValidationError("LANG Exception: resultset has not been set", None)

        #metadata defines the data, so we iterate over the metadata and use it to extract columns from our resultset. If the column data is null then we need to check
        #either the metadata defintion or the source data. 
        for meta in self.metaData:
            colData = SQLTools.getCol(self.rs, meta)
            if ( (not colData is None) and (len(colData[meta]) > 0) ):
                self.validateList(colData, self.metaData[meta])
     
            else:
                #In the case of null data, we throw an exception so it can be addressed immediately. You might want to change this to just log an error and continue 
                #in a future build this behaviour would be controlled at runtime via a switch.
                raise ValidationError("LANG Exception: Could not locate column '" + col + "' in resultset", None)
                
            
    def validateList(self:object, colData:dict, meta:dict):

        """
        Execute a series of validations against the supplied column of data and the metadata for the column.
        Which validation is run is determined by entries in the metadata.
        """        
        # As there is only one column in the dictionay, obtain that column
        key = next(iter(colData))
        col = colData[key]
        
        for value in col:
            self.checkMandatory(meta, key, value)                  
            self.checkSize(meta, key, value)
            self.checkType(meta, key, value)
            self.checkEnum(meta, key, value)
            self.checkStartsWith(meta, key, value)
            self.checkFormat(meta, key, value)                        
            self.checkUnique(meta, col, key, value)

        self.checkComposite(meta, key)            
        # expression evaluation is different to processing field specific validations as it could link in other columns from the resultset
        self.evaluateExpression(meta, key)
        
        # gather some statistical measurememnts for our column
        self.profileData(meta, col, key)
            
        
    def checkMandatory(self, meta:dict, key:str, value:str):
        # mandatory field check
        if (Validator.isTrue(meta, "Mandatory") ):
            if ( (Validator.isBlankOrNull(value)) and (not Validator.isAllowBlank(meta)) ):
                self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.MANDATORYCOMPLETENESS.value,description="Error: Mandatory field is BLANK or NULL. A value is required."))                             
        else:
            # optional field check. According to LANG optional fields shpuld contain some sort of default value
            # i.e. no field shpould ever be blank or NULL.
            if ( (Validator.isBlankOrNull(value)) and (not Validator.isAllowBlank(meta)) ):
                self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.OPTIONALCOMPLETENESS.value, description="Error: Optional field is BLANK or NULL. A default value is required."))
                
            
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
                    self.addMeasurement(Measurement(keyStr,errorCategory=MeasurementCategory.UNIQUENESSCOMPOSITE.value, description="Error: Duplicate composite key: '" + keyStr + "', value: '" + s + "'"))
                else:
                    seen.append(s)
               
                        
    def checkSize(self, meta:dict, key:str, value:str):
        # field length check
        if (Validator.exists(meta, "Size")):
            if ( (len(value) > int(meta["Size"])) and (not Validator.isBlankOrNull(value)) ):
                self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.METACOMPLIANCESIZE.value, description="Error: Value '" + value + "' is longer than size '" + str(meta["Size"]) + "'"))
                
            
    def checkType(self, meta:dict, key:str, value:str):
        # field type check
        isValidType = True
        
        if (Validator.exists(meta, "Type")):
            if (meta["Type"]=="int"):
                if ( (Validator.isBlankOrNull(value)) or (not Validator.isInt(value)) ):
                    if (not Validator.isAllowBlank(meta)):
                        self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.METACOMPLIANCETYPE.value, description="Error: Value '" + value + "' is not an int. An int was expected"))
                        isValidType = False
            elif (meta["Type"]=="float"):
                if ( (Validator.isBlankOrNull(value)) or (not Validator.isFloat(value)) ): 
                    if (not Validator.isAllowBlank(meta)):
                        self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.METACOMPLIANCETYPE.value, description="Error: Value '" + value + "' is not a float. A float was expected"))
                        isValidType = False
                
        # given that min and max checks only apply to int and float values we may as well test for them now
        if (isValidType):
            self.checkMinMax(meta, key, value)
            

    def checkMinMax(self, meta:dict, key:str, value:str):
        # field value range check (int and float only although in theory we could specify min and max ranges for other attributes)
        min = -1
        max = -1
        val = -1
        default = -1
        
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

        if (Validator.exists(meta, "Default")):
            try:
                default = float(meta["Default"])
            except Exception as e:
                pass

        try:
            val = float(value)
        except Exception as e:
            pass

        if (min != -1):
            if (val != -1 and val < min and val != default):
                # error
                self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.METACOMPLIANCERANGEMIN.value, description="Error: Value '" + value + "' must be >= " + str(min)))
            
                
        if (max != -1):
            if (val != -1 and val > max and val != default):
                # error
                self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.METACOMPLIANCERANGEMAX.value, description="Error: Value '" + value + "' must be <= " + str(max)))
            

    def checkEnum(self, meta:dict, key:str, value:str):
        # enumerated field check
        if (Validator.exists(meta, "Enum")):
            # enum is expected to be a list
            enum = meta["Enum"]
            
            # check that the value exists within the provided list. If the value is blank then ignore it 
            # as we should have picked it up in the mandatory/optional test anyway
            # (i.e. if the field is optional but a value has been provided then we check it against the supplied list)
            if ( (len(value)>0) and (value not in enum) and (value != "(Null)") ):
                self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.METACOMPLIANCEENUM.value, description="Error: Value '" + value + "' is outside the enumeration set '" + enum + "'"))



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
                    self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.FORMATCONSISTENCYPREFIX.value, description="Error: Value '" + value + "' does not begin with any of: '" + str(startsWith) + "'"))


            
    def checkFormat(self, meta:dict, key:str, value:str):
        # format check (must provide a regex)
        if (Validator.exists(meta, "Format")):
            re.purge()
            isMatch = (not re.match(meta["Format"], value) is None)
            if ( (not isMatch) and (not Validator.isAllowBlank(meta)) ):
                self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.FORMATCONSISTENCY.value, description="Error: Value '" + value + "' does not match regex '" + meta["Format"] + "'"))
            

            
    def checkUnique(self, meta:dict, row:list, key:str, value:str):
        # unique field check
        if (Validator.isTrue(meta, "Unique")):
            # sum the number of times value appears in the row. this is faster than using list.count(value)
            counter = sum(1 for i in row if str(i) == value)
            
            # create a list with every entry of value in the row. If there are duplicates then the resulting list will have >1 entries
            if (counter>1):
                self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.UNIQUENESS.value, description="Error: Value '" + value + "' is not UNIQUE. A unique value was expected"))


            
    def evaluateExpression(self, meta:dict, key:str):
        # evaluate any custom expressions
        if (Validator.exists(meta, "Expression")):
            expr = meta["Expression"]
            
            # %1 is a placeholder for whatever the column name is owning the expression (it's just a shortcut)
            expr = expr.replace("%1", "[" + key + "]")
            exp = ExpressionBuilder()
            
            fields = exp.parseExpr(expr)
            colData = dict()
            
            # grab all of the columns that we need and store in a local dict
            for field in fields:
                
                # grab the column data out of the resultset
                values = SQLTools.getCol(self.rs, field)
                
                # if the column couldn't be found then we have a configuration issue so raise an exception
                if (values is None):
                    raise ValidationError("Error evaluating expression: '" + expr + "'. Unable to find column '" + field + "' in the resultset", None)
                
                colData.update(values)
            
            # convert the seperate columns into an array of name,value pairs
            pairs=[dict(zip(colData, col)) for col in zip(*colData.values())]
            
            for pair in pairs:
                result=None
                ev = exp.merge(expr,pair)
                
                try:
                    result = eval(ev)
                except Exception as e:
                    #print("Warning: An error occured while evaluating expression: '" + ev + "': " + str(e))
                    
                    self.addMeasurement(Measurement(expr,errorCategory=MeasurementCategory.RULECOMPLIANCE.value, description="Error: Expression '" + ev + "' returned an error '" + str(e) + "'"))

                if ( (not result is None) and (result == False) ):
                    self.addMeasurement(Measurement(expr,errorCategory=MeasurementCategory.RULECOMPLIANCE.value, description="Error: Expression '" + ev + "' returned FALSE"))

    
