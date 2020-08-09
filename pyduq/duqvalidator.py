import re
import time
from pyduq.metautils import MetaUtils
from pyduq.abstractduqvalidator import AbstractDUQValidator
from pyduq.patterns import Patterns
from pyduq.duqerror import ValidationError
from pyduq.dataqualityerror import DataQualityError, DataQualityDimension
from pyduq.expressionbuilder import ExpressionBuilder
from pyduq.SQLTools import SQLTools
from pyduq.dataprofile import DataProfile

 
class DUQValidator(AbstractDUQValidator):
    """ DUQValidator: A generic validator for LANG. 
    The main execution method is validate().
    """   
        
    def validate(self:object, customValidator:str):
        """
        Validate a resultset against predefined metadata based on the LANG rules of data quality.
        """
        if (self.metadata is None):
            raise ValidationError("LANG Exception: meta-data has not been set", None)
        elif (self.dataset is None):
            raise ValidationError("LANG Exception: resultset has not been set", None)

        """
        Execute a series of validations against the supplied column of data and the metadata for the column.
        Which validation is run is determined by entries in the metadata.
        """         
        for meta_attribute_key, meta_attribute_definition in self.metadata.items():                
            if (meta_attribute_key in self.dataset):
                print("Validating attribute \t'" + meta_attribute_key + "'...", end='\r')
                
                attribute = self.dataset[meta_attribute_key]
                
                for value in attribute:
                    self.checkMandatory(meta_attribute_definition, meta_attribute_key, value)                  
                    self.checkSize(meta_attribute_definition, meta_attribute_key, value)
                    self.checkType(meta_attribute_definition, meta_attribute_key, value)
                    self.checkEnum(meta_attribute_definition, meta_attribute_key, value)
                    self.checkStartsWith(meta_attribute_definition, meta_attribute_key, value)
                    
                self.checkFormat(meta_attribute_definition, meta_attribute_key)          
                self.checkUnique(meta_attribute_definition, meta_attribute_key)
             
                self.checkComposite(meta_attribute_definition, meta_attribute_key)            
                # expression evaluation is different to processing field specific validations as it could link in other columns from the resultset
                self.evaluateExpression(meta_attribute_definition, meta_attribute_key)

                print("Validating attribute \t'" + meta_attribute_key + "'...\t\t..Complete.")
            else:
                self.addDataQualityError(DataQualityError(meta_attribute_key, error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Attribute '" + meta_attribute_key + "' was not found in the dataset."))
        
        # only invoke the custom validator if one has been provoded
        if (not customValidator is None and len(customValidator) > 0):
            self.customValidator(customValidator)
        
        
    def checkMandatory(self, meta_attribute_definition:dict, meta_attribute_key:str, value:str):
        # mandatory field check
        if (MetaUtils.isTrue(meta_attribute_definition, "Mandatory") ):
            if ( (MetaUtils.isBlankOrNull(value)) and (not MetaUtils.isAllowBlank(meta_attribute_definition)) ):
                self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.COMPLETENESSMANDATORY.value,description="Error: Mandatory field is BLANK or NULL. A value is required."))                             
        else:
            # optional field check. According to LANG optional fields shpuld contain some sort of default value
            # i.e. no field shpould ever be blank or NULL.
            if ( (MetaUtils.isBlankOrNull(value)) and (not MetaUtils.isAllowBlank(meta_attribute_definition)) ):
                self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.COMPLETENESSOPTIONAL.value, description="Error: Optional field is BLANK or NULL. A default value is required."))
                
            
    def checkComposite(self, meta_attribute_definition:dict, meta_attribute_key:str):
        # unique field check
        if (MetaUtils.exists(meta_attribute_definition, "Composite")):
            # sum the number of times value appears in the row. this is faster than using list.count(value)
            list_of_attribute_keys = meta_attribute_definition["Composite"]
            # Concatenate the list of attribute_keys into a composite meta_attribute_key string
            attribute_keys = '+'.join(map(str, list_of_attribute_keys))
            attribute_keys = attribute_keys.replace("%1", meta_attribute_key)
        
        
            # populate a dictionary of just the values that are required to create the composite meta_attribute_key
            attribute_data={}
            for col in list_of_attribute_keys:
                col = col.replace("%1", meta_attribute_key)
                attribute_data[col]=SQLTools.getColValues(self.dataset, col)
            
            seen=set()
            rowindex=0
            # convert the dictionary of columns into a list of tuples
            fields=[dict(zip(attribute_data, col)) for col in zip(*attribute_data.values())]
            
            # check to see if there is are any duplicates in the order of attribute_keys provided
            for row in fields:
                # join the values from the columns that make up the composite meta_attribute_key to form a single value
                s = ''.join(map(str, row.values()))
                if (s in seen):
                    self.addDataQualityError(DataQualityError(attribute_keys,error_dimension=DataQualityDimension.UNIQUENESS.value, description="Error: Duplicate composite meta_attribute_key: '" + attribute_keys + "', value: '" + s + "'"))
                else:
                    seen.add(s)
               
                        
    def checkSize(self, meta_attribute_definition:dict, meta_attribute_key:str, value:str):
        # field length check
        if (MetaUtils.exists(meta_attribute_definition, "Size")):
            if ( (len(value) > int(meta_attribute_definition["Size"])) and (not MetaUtils.isBlankOrNull(value)) ):
                self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Value '" + value + "' is longer than size '" + str(meta_attribute_definition["Size"]) + "'"))
                
            
    def checkType(self, meta_attribute_definition:dict, meta_attribute_key:str, value:str):
        # field type check
        is_valid_type = True

        if (MetaUtils.exists(meta_attribute_definition, "Type")):
            # if a default value has been specified then ignore the type check if the value matches the default
            if (MetaUtils.exists(meta_attribute_definition, "Default")):
                if (value==meta_attribute_definition["Default"]):
                    is_valid_type = False
            
            if (meta_attribute_definition["Type"] in ["int","integer"]):
                if ( (MetaUtils.isBlankOrNull(value)) or (not MetaUtils.isInt(value)) ):
                    if (not MetaUtils.isAllowBlank(meta_attribute_definition)):
                        self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Value '" + value + "' is not an int. An int was expected"))
                        is_valid_type = False
            elif (meta_attribute_definition["Type"] in ["float","number"]):
                if ( (MetaUtils.isBlankOrNull(value)) or (not MetaUtils.isFloat(value)) ): 
                    if (not MetaUtils.isAllowBlank(meta_attribute_definition)):
                        self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Value '" + value + "' is not a float. A float was expected"))
                        is_valid_type = False
            elif (meta_attribute_definition["Type"] in ["bool","boolean"]):
                if ( (MetaUtils.isBlankOrNull(value)) or (not value.lower() in ["false", "true", "f", "t", "n", "y", "no", "yes", "0", "1"]) ): 
                    if (not MetaUtils.isAllowBlank(meta_attribute_definition)):
                        self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Value '" + value + "' is not a boolean. A boolean was expected"))
                        is_valid_type = False
                    
            # given that min and max checks only apply to int and float values we may as well test for them now
            if (is_valid_type):
                self.checkMinMax(meta_attribute_definition, meta_attribute_key, value)
                

    def checkMinMax(self, meta_attribute_definition:dict, meta_attribute_key:str, value:str):
        # field value range check (int and float only although in theory we could specify min and max ranges for other attributes)
        min = -1
        max = -1
        val = -1
        default = -1
        
        if (MetaUtils.exists(meta_attribute_definition, "Min")):
            try:
                min = float(meta_attribute_definition["Min"])
            except Exception as e:
                pass
        
        if (MetaUtils.exists(meta_attribute_definition, "Max")):
            try:
                max = float(meta_attribute_definition["Max"])
            except Exception as e:
                pass

        if (MetaUtils.exists(meta_attribute_definition, "Default")):
            try:
                default = float(meta_attribute_definition["Default"])
            except Exception as e:
                pass

        try:
            val = float(value)
        except Exception as e:
            pass

        if (min != -1):
            if (val != -1 and val < min and val != default):
                # error
                self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Value '" + value + "' must be >= " + str(min)))
            
                
        if (max != -1):
            if (val != -1 and val > max and val != default):
                # error
                self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Value '" + value + "' must be <= " + str(max)))
            

    def checkEnum(self, meta_attribute_definition:dict, meta_attribute_key:str, value:str):
        # enumerated field check
        if (MetaUtils.exists(meta_attribute_definition, "Enum")):
            # enum is expected to be a list
            enum = meta_attribute_definition["Enum"]
            
            # check that the value exists within the provided list. If the value is blank then ignore it 
            # as we should have picked it up in the mandatory/optional test anyway
            # (i.e. if the field is optional but a value has been provided then we check it against the supplied list)
            if ( (len(value)>0) and (value not in enum) and (value != "(Null)") ):
                self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Value '" + value + "' is outside the enumeration set '" + str(enum) + "'"))



    def checkStartsWith(self, meta_attribute_definition:dict, meta_attribute_key:str, value:str):
        # enumerated field check
        if (MetaUtils.exists(meta_attribute_definition, "StartsWith")):
            # startsWith is expected to be a list
            startsWith = meta_attribute_definition["StartsWith"]
            
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
                    self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.FORMATCONSISTENCY.value, description="Error: Value '" + value + "' does not begin with any of: '" + str(startsWith) + "'"))


            
    def checkFormat(self, meta_attribute_definition:dict, meta_attribute_key:str):
        # format check (must provide a regex)
        if (MetaUtils.exists(meta_attribute_definition, "Format")):
            re.purge()
            regex=re.compile(meta_attribute_definition["Format"])
            
            for value in self.dataset[meta_attribute_key]:
                #isMatch = (not re.match(meta_attribute_definition["Format"], value) is None)
                isMatch = (not regex.match(value) is None)
                
                if ( (not isMatch) and (not MetaUtils.isAllowBlank(meta_attribute_definition)) ):
                    self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.FORMATCONSISTENCY.value, description="Error: Value '" + value + "' does not match regex #'" + meta_attribute_definition["Format"] + "'"))
                    
            

   
    def checkUnique(self, meta_attribute_definition:dict, meta_attribute_key:str):
        # unique field check
        if (MetaUtils.isTrue(meta_attribute_definition, "Unique")):
            # quick count the number of times values occurs in the column. Assumes possibly sorted so breaks the loop if >1 occurences to save time0

            sorted_data = sorted(self.dataset[meta_attribute_key])
            seen = set()           

            for i in range(len(sorted_data)):
                counter = 0

                value = sorted_data[i]
                
                if (not value in seen):
                    seen.add(value) #only process a value once 
                    
                    j = i
                    
                    while ( (j < len(sorted_data)) and (sorted_data[j] == value) ):
                        counter +=1
                        j+=1
                    
                    if (counter>1):
                        self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.UNIQUENESS.value, description="Error: Value '" + value + "' is not UNIQUE. A unique value was expected"))


            
    def evaluateExpression(self, meta_attribute_definition:dict, meta_attribute_key:str):
        # evaluate any custom expressions
        if (MetaUtils.exists(meta_attribute_definition, "Expression")):
            expr = meta_attribute_definition["Expression"]
            
            # %1 is a placeholder for whatever the column name is owning the expression (it's just a shortcut)
            expr = expr.replace("%1", "[" + meta_attribute_key + "]")
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
                    self.addDataQualityError(DataQualityError(expr,error_dimension=DataQualityDimension.BUSINESSRULECOMPLIANCE.value, description="Error: Expression '" + ev + "' returned an error '" + str(e) + "'"))
                    result=None

                if ( (not result is None) and (result == False) ):
                    self.addDataQualityError(DataQualityError(expr,error_dimension=DataQualityDimension.BUSINESSRULECOMPLIANCE.value, description="Error: Expression '" + ev + "' returned FALSE"))

    