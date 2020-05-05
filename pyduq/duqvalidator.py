import re
import time
from pyduq.metautils import MetaUtils
from pyduq.AbstractDUQValidator import AbstractDUQValidator
from pyduq.patterns import Patterns
from pyduq.langerror import ValidationError
from pyduq.measurement import Measurement, MeasurementCategory
from pyduq.expressionbuilder import ExpressionBuilder
from pyduq.SQLTools import SQLTools
from pyduq.dataprofile import DataProfile

 
class DUQValidator(AbstractDUQValidator):
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
        elif (self.dataset is None):
            raise ValidationError("LANG Exception: resultset has not been set", None)

        #metadata defines the data, so we iterate over the metadata and use it to extract columns from our resultset. If the column data is null then we need to check
        #either the metadata defintion or the source data. 
        for metaAttributeKey in self.metaData:                
            if (metaAttributeKey in self.dataset):
                self.validateList(metaAttributeKey)
            else:
                #In the case of null data, we throw an exception so it can be addressed immediately. You might want to change this to just log an error and continue 
                #in a future build this behaviour would be controlled at runtime via a switch.
                raise ValidationError("LANG Exception: Could not locate attribute '" + col + "' in resultset", None)
                        
    def validateList(self:object, key:str):

        """
        Execute a series of validations against the supplied column of data and the metadata for the column.
        Which validation is run is determined by entries in the metadata.
        """        
        # As there is only one column in the dictionay, obtain that column
        
        for value in self.dataset[key]:
            self.checkMandatory(self.metaData[key], key, value)                  
            self.checkSize(self.metaData[key], key, value)
            self.checkType(self.metaData[key], key, value)
            self.checkEnum(self.metaData[key], key, value)
            self.checkStartsWith(self.metaData[key], key, value)
            self.checkFormat(self.metaData[key], key, value)                        
            self.checkUnique(self.metaData[key], key, value)

        self.checkComposite(self.metaData[key], key)            
        # expression evaluation is different to processing field specific validations as it could link in other columns from the resultset
        self.evaluateExpression(self.metaData[key], key)
        
        # gather some statistical measurememnts for our column
        self.profileData(self.metaData[key], self.dataset[key], key)
            
        
    def checkMandatory(self, metaAttributeDefinition:dict, key:str, value:str):
        # mandatory field check
        if (MetaUtils.isTrue(metaAttributeDefinition, "Mandatory") ):
            if ( (MetaUtils.isBlankOrNull(value)) and (not MetaUtils.isAllowBlank(metaAttributeDefinition)) ):
                self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.MANDATORYCOMPLETENESS.value,description="Error: Mandatory field is BLANK or NULL. A value is required."))                             
        else:
            # optional field check. According to LANG optional fields shpuld contain some sort of default value
            # i.e. no field shpould ever be blank or NULL.
            if ( (MetaUtils.isBlankOrNull(value)) and (not MetaUtils.isAllowBlank(metaAttributeDefinition)) ):
                self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.OPTIONALCOMPLETENESS.value, description="Error: Optional field is BLANK or NULL. A default value is required."))
                
            
    def checkComposite(self, metaAttributeDefinition:dict, key:str):
        # unique field check
        if (MetaUtils.exists(metaAttributeDefinition, "Composite")):
            # sum the number of times value appears in the row. this is faster than using list.count(value)
            listOfKeys = metaAttributeDefinition["Composite"]
            # Concatenate the list of keys into a composite key string
            keyStr = '+'.join(map(str, listOfKeys))
            keyStr = keyStr.replace("%1", key)
        
            # populate a dictionary of just the values that are required to create the composite key
            keyData=dict()
            for col in listOfKeys:
                col = col.replace("%1", key)
                keyData[col]=SQLTools.getColValues(self.dataset, col)
            
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
               
                        
    def checkSize(self, metaAttributeDefinition:dict, key:str, value:str):
        # field length check
        if (MetaUtils.exists(metaAttributeDefinition, "Size")):
            if ( (len(value) > int(metaAttributeDefinition["Size"])) and (not MetaUtils.isBlankOrNull(value)) ):
                self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.METACOMPLIANCESIZE.value, description="Error: Value '" + value + "' is longer than size '" + str(metaAttributeDefinition["Size"]) + "'"))
                
            
    def checkType(self, metaAttributeDefinition:dict, key:str, value:str):
        # field type check
        isValidType = True

        if (MetaUtils.exists(metaAttributeDefinition, "Type")):
            # if a default value has been specified then ignore the type check if the value matches the default
            if (MetaUtils.exists(metaAttributeDefinition, "Default")):
                if (value==metaAttributeDefinition["Default"]):
                    pass
            else:
                if (metaAttributeDefinition["Type"]=="int"):
                    if ( (MetaUtils.isBlankOrNull(value)) or (not MetaUtils.isInt(value)) ):
                        if (not MetaUtils.isAllowBlank(metaAttributeDefinition)):
                            self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.METACOMPLIANCETYPE.value, description="Error: Value '" + value + "' is not an int. An int was expected"))
                            isValidType = False
                elif (metaAttributeDefinition["Type"]=="float"):
                    if ( (MetaUtils.isBlankOrNull(value)) or (not MetaUtils.isFloat(value)) ): 
                        if (not MetaUtils.isAllowBlank(metaAttributeDefinition)):
                            self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.METACOMPLIANCETYPE.value, description="Error: Value '" + value + "' is not a float. A float was expected"))
                            isValidType = False
                    
                # given that min and max checks only apply to int and float values we may as well test for them now
                if (isValidType):
                    self.checkMinMax(metaAttributeDefinition, key, value)
                

    def checkMinMax(self, metaAttributeDefinition:dict, key:str, value:str):
        # field value range check (int and float only although in theory we could specify min and max ranges for other attributes)
        min = -1
        max = -1
        val = -1
        default = -1
        
        if (MetaUtils.exists(metaAttributeDefinition, "Min")):
            try:
                min = float(metaAttributeDefinition["Min"])
            except Exception as e:
                pass
        
        if (MetaUtils.exists(metaAttributeDefinition, "Max")):
            try:
                max = float(metaAttributeDefinition["Max"])
            except Exception as e:
                pass

        if (MetaUtils.exists(metaAttributeDefinition, "Default")):
            try:
                default = float(metaAttributeDefinition["Default"])
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
            

    def checkEnum(self, metaAttributeDefinition:dict, key:str, value:str):
        # enumerated field check
        if (MetaUtils.exists(metaAttributeDefinition, "Enum")):
            # enum is expected to be a list
            enum = metaAttributeDefinition["Enum"]
            
            # check that the value exists within the provided list. If the value is blank then ignore it 
            # as we should have picked it up in the mandatory/optional test anyway
            # (i.e. if the field is optional but a value has been provided then we check it against the supplied list)
            if ( (len(value)>0) and (value not in enum) and (value != "(Null)") ):
                self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.METACOMPLIANCEENUM.value, description="Error: Value '" + value + "' is outside the enumeration set '" + str(enum) + "'"))



    def checkStartsWith(self, metaAttributeDefinition:dict, key:str, value:str):
        # enumerated field check
        if (MetaUtils.exists(metaAttributeDefinition, "StartsWith")):
            # startsWith is expected to be a list
            startsWith = metaAttributeDefinition["StartsWith"]
            
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


            
    def checkFormat(self, metaAttributeDefinition:dict, key:str, value:str):
        # format check (must provide a regex)
        if (MetaUtils.exists(metaAttributeDefinition, "Format")):
            re.purge()
            isMatch = (not re.match(metaAttributeDefinition["Format"], value) is None)
            if ( (not isMatch) and (not MetaUtils.isAllowBlank(metaAttributeDefinition)) ):
                self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.FORMATCONSISTENCY.value, description="Error: Value '" + value + "' does not match regex '" + metaAttributeDefinition["Format"] + "'"))
            

            
    def checkUnique(self, metaAttributeDefinition:dict, key:str, value:str):
        # unique field check
        if (MetaUtils.isTrue(metaAttributeDefinition, "Unique")):
            # sum the number of times value appears in the row. this is faster than using list.count(value)
            counter = sum(1 for i in self.dataset[key] if str(i) == value)
            
            # create a list with every entry of value in the row. If there are duplicates then the resulting list will have >1 entries
            if (counter>1):
                self.addMeasurement(Measurement(key,errorCategory=MeasurementCategory.UNIQUENESS.value, description="Error: Value '" + value + "' is not UNIQUE. A unique value was expected"))


            
    def evaluateExpression(self, metaAttributeDefinition:dict, key:str):
        # evaluate any custom expressions
        if (MetaUtils.exists(metaAttributeDefinition, "Expression")):
            expr = metaAttributeDefinition["Expression"]
            
            # %1 is a placeholder for whatever the column name is owning the expression (it's just a shortcut)
            expr = expr.replace("%1", "[" + key + "]")
            exp = ExpressionBuilder()
            
            fields = exp.parseExpr(expr)
            colData = dict()
            
            # grab all of the columns that we need and store in a local dict
            for field in fields:
                
                # grab the column data out of the resultset
                values = SQLTools.getCol(self.dataset, field)
                
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
                    self.addMeasurement(Measurement(expr,errorCategory=MeasurementCategory.RULECOMPLIANCE.value, description="Error: Expression '" + ev + "' returned an error '" + str(e) + "'"))
                    result=None

                if ( (not result is None) and (result == False) ):
                    self.addMeasurement(Measurement(expr,errorCategory=MeasurementCategory.RULECOMPLIANCE.value, description="Error: Expression '" + ev + "' returned FALSE"))

    