import re
import time
from collections import Counter
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
        
    def validate(self:object, customValidator:str=None):
        """
        Validate a resultset against predefined metadata based on the LANG rules of data quality.
        """
        if (self.metadata is None):
            raise ValidationError("LANG Exception: meta-data has not been set", None)
        elif (self.dataset is None):
            raise ValidationError("LANG Exception: resultset has not been set", None)

        """
        Change request: find and output the primary key in the error report file if specified
        """
        primary_key = ""
        primary_key_values = None
        
        for key, item in self.metadata.items():                
            if (MetaUtils.isTrue(item, "PrimaryKey")):
                primary_key = key
                primary_key_values = self.dataset[primary_key]
                break
                
        """
        Execute a series of validations against the supplied column of data and the metadata for the column.
        Which validation is run is determined by entries in the metadata.
        """         
        for meta_attribute_key, meta_attribute_definition in self.metadata.items():                
            if (meta_attribute_key in self.dataset):
                print("Validating attribute \t'" + meta_attribute_key + "'...", end='\r')
                                
                attribute = self.dataset[meta_attribute_key]
                                
                for row_count in range(len(attribute)):
                    value = attribute[row_count]
                    
                    """ 
                    If a primarykey tag has been found then output the value so that the user 
                     has a reference to search for the record in the source system. 
                     If there is no primary key attribute set then output the row count 
                    """
                    
                    if (not primary_key_values is None):
                        primary_key_value = primary_key_values[row_count]
                    else:
                        primary_key_value = "Row: " + str(row_count+1)
                    
                    self.checkMandatory(meta_attribute_definition, meta_attribute_key, value, primary_key_value)                  
                    self.checkSize(meta_attribute_definition, meta_attribute_key, value, primary_key_value)
                    self.checkType(meta_attribute_definition, meta_attribute_key, value, primary_key_value)
                    self.checkEnum(meta_attribute_definition, meta_attribute_key, value, primary_key_value)
                    self.checkStartsWith(meta_attribute_definition, meta_attribute_key, value, primary_key_value)

                
                # format check (must provide a regex)
                if (MetaUtils.exists(meta_attribute_definition, "Format")):
                        re.purge()
                        regex=re.compile(meta_attribute_definition["Format"])
                        
                        for row_count in range(len(attribute)):
                            if (not primary_key_values is None):
                                primary_key_value = primary_key_values[row_count]
                            else:
                                primary_key_value = "Row: " + str(row_count+1)
                        
                            value = attribute[row_count]
                            #if the value is blank then ignore it
                            
                            if ( not (MetaUtils.isBlankOrNull(value))) :
                            
                                isMatch = (not regex.match(value) is None)
                            
                                if (not isMatch):
                                    self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.FORMATCONSISTENCY.value, description="Error: Value '" + value + "' does not match regex #'" + meta_attribute_definition["Format"] + "'"))

                   
                # unique field check        
                if (MetaUtils.isTrue(meta_attribute_definition, "Unique") ):
                    # quick count the number of times values occurs in the column. Assumes possibly sorted so breaks the loop if >1 occurences to save time0
                    seen = set()          

                    for row_count in range(len(attribute)):
                        if (not primary_key_values is None):
                            primary_key_value = primary_key_values[row_count]
                        else:
                            primary_key_value = "Row: " + str(row_count+1)
                    
                        value = attribute[row_count]

                        if (not value in seen):
                            seen.add(value) #only process a value once 
                        else:    
                            self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.UNIQUENESS.value, description="Error: Value '" + value + "' is not UNIQUE. A unique value was expected."))
                            
                self.checkComposite(meta_attribute_definition, meta_attribute_key)
                self.checkNonRepeatingGroups(meta_attribute_definition, meta_attribute_key)
                
                # expression evaluation is different to processing field specific validations as it could link in other columns from the resultset
                self.evaluateExpression(meta_attribute_definition, meta_attribute_key)

                print("Validating attribute \t'" + meta_attribute_key + "'...\t\t..Complete.")
            else:
                self.addDataQualityError(DataQualityError(meta_attribute_key, error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Attribute '" + meta_attribute_key + "' was not found in the dataset."))
        
        # only invoke the custom validator if one has been provoded
        if (not customValidator is None and len(customValidator) > 0):
            self.customValidator(customValidator)
        
        
    def checkMandatory(self, meta_attribute_definition:dict, meta_attribute_key:str, value:str, primary_key_value:str):
        # mandatory field check
        if (MetaUtils.isTrue(meta_attribute_definition, "Mandatory") ):
            if ( (MetaUtils.isBlankOrNull(value)) and (not MetaUtils.isAllowBlank(meta_attribute_definition)) ):
                self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.COMPLETENESSMANDATORY.value,description="Error: Mandatory field is BLANK or NULL. A value is required.", primary_key_value=primary_key_value))                             
        else:
            # optional field check. According to LANG optional fields shpuld contain some sort of default value
            # i.e. no field shpould ever be blank or NULL.
            if ( (MetaUtils.isBlankOrNull(value)) and (not MetaUtils.isAllowBlank(meta_attribute_definition)) ):
                self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.COMPLETENESSOPTIONAL.value, description="Error: Optional field is BLANK or NULL. A default value is required.", primary_key_value=primary_key_value))
                
            
    def checkComposite(self, meta_attribute_definition:dict, meta_attribute_key:str):
        # unique field check
        if (MetaUtils.exists(meta_attribute_definition, "Composite")):
            # sum the number of times value appears in the row. this is faster than using list.count(value)
            list_of_attribute_keys = meta_attribute_definition["Composite"]
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
                composite_key = '|'.join(map(str, row.values()))
                if (composite_key in seen):
                    self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.UNIQUENESS.value, description="Error: Duplicate composite meta_attribute_key: '" + attribute_keys + "', values: '" + composite_key + "'", primary_key_value=composite_key))
                else:
                    seen.add(composite_key)

               
    def checkNonRepeatingGroups(self, meta_attribute_definition:dict, meta_attribute_key:str):
        '''
            This method is for a very specific use case - to find all non-repeting groups of Y,Z,... in repeating groups of X.
            
            The scenario is used in situations where you have sub-groups of records within the data set, that ought to be identical across
            all columns, and you need to know when something is different. Image you have the same col existing in more than one entity. You write
            a query to flatten the entities into a single table. From there, you want to ensure that this repeated attributes are the same (like a person's name
            or email address) across the entities. That's what this method is for!
            
            Given attributes X,Y,Z,...:
            Find all the repeating groups of X
            For each repeating group:
                Find all occurences where Y and Z are different (i.e. non-unique)
                If all instances of X-Y-X are identical then this is considered a repeating group and is not a rule violation and thus ignored
                
            Note: Use %1 to indicate which field is X 
            
            The non-repeating group (X) must be the first attribute in the list. 
        '''
        
        if (MetaUtils.exists(meta_attribute_definition, "NonRepeatingGroup")):
            # sum the number of times value appears in the row. this is faster than using list.count(value)
            list_of_attribute_keys = meta_attribute_definition["NonRepeatingGroup"]
            
            if (len(list_of_attribute_keys) < 2):
                raise ValidationError("LANG Exception: " + meta_attribute_key + " - NonRepeatingGroup tag requires at least 2 attributes to be defined. Please refer to the documentation.", None)
            
            attribute_keys = '+'.join(map(str, list_of_attribute_keys))
            attribute_keys = attribute_keys.replace("%1", meta_attribute_key)

            # populate a dictionary of just the values that are required to create the non-repeating group meta_attribute_key
            attribute_data={}
            for col in list_of_attribute_keys:
                col = col.replace("%1", meta_attribute_key)
                attribute_data[col]=SQLTools.getColValues(self.dataset, col)
                                   
            # convert the dictionary of columns into a list of tuples
            fields=[dict(zip(attribute_data, col)) for col in zip(*attribute_data.values())]
            
            # find all the repeating values (X in our speudo code above)
            x_groups_count = Counter(attribute_data[meta_attribute_key])
            
            # iterate through the repeating groups of X values, ignore any single row counts
            for value, count in x_groups_count.items():
                if (count>1):
                    seen={}
                    rowindex=0
                    
                    # find records whose starting row valu ematches the repeating group value
                    for row in fields:
                        val = next(iter(row.values()))
                        
                        if (val == value):
                            non_group = list(row.values())
                            
                            # join the values from the columns that make up the composite meta_attribute_key to form a single value
                            nonrepeatinggroup_key = '|'.join(map(str, non_group))
                            if (not nonrepeatinggroup_key in seen.values()):
                                seen[str(rowindex)+":"+str(value)]=nonrepeatinggroup_key
                                rowindex+=1
             
                    # only output to the error file if we have more than 1 row 
                    if (rowindex > 1):
                        for nonrepeatinggroup_key, value in seen.items():
                            self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.UNIQUENESS.value, description="Error: Non-repeating group found.  meta_attribute_key: '" + nonrepeatinggroup_key + "-> " + attribute_keys + "', values: '" + value + "'", primary_key_value=meta_attribute_key))           
           
                        
    def checkSize(self, meta_attribute_definition:dict, meta_attribute_key:str, value:str, primary_key_value:str):
        # field length check
        if (MetaUtils.exists(meta_attribute_definition, "Size")):
            if ( (len(value) > int(meta_attribute_definition["Size"])) and (not MetaUtils.isBlankOrNull(value)) ):
                self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Value '" + value + "' is longer than size '" + str(meta_attribute_definition["Size"]) + "'", primary_key_value=primary_key_value))
                
            
    def checkType(self, meta_attribute_definition:dict, meta_attribute_key:str, value:str, primary_key_value:str):
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
                        self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Value '" + value + "' is not an int. An int was expected",primary_key_value=primary_key_value))
                        is_valid_type = False
            elif (meta_attribute_definition["Type"] in ["float","number"]):
                if ( (MetaUtils.isBlankOrNull(value)) or (not MetaUtils.isFloat(value)) ): 
                    if (not MetaUtils.isAllowBlank(meta_attribute_definition)):
                        self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Value '" + value + "' is not a float. A float was expected",primary_key_value=primary_key_value))
                        is_valid_type = False
            elif (meta_attribute_definition["Type"] in ["bool","boolean"]):
                if ( (MetaUtils.isBlankOrNull(value)) or (not value.lower() in ["false", "true", "f", "t", "n", "y", "no", "yes", "0", "1"]) ): 
                    if (not MetaUtils.isAllowBlank(meta_attribute_definition)):
                        self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Value '" + value + "' is not a boolean. A boolean was expected",primary_key_value=primary_key_value))
                        is_valid_type = False
                    
            # given that min and max checks only apply to int and float values we may as well test for them now
            if (is_valid_type):
                self.checkMinMax(meta_attribute_definition, meta_attribute_key, value, primary_key_value)
                

    def checkMinMax(self, meta_attribute_definition:dict, meta_attribute_key:str, value:str, primary_key_value:str):
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
                self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Value '" + value + "' must be >= " + str(min), primary_key_value=primary_key_value))
            
                
        if (max != -1):
            if (val != -1 and val > max and val != default):
                # error
                self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Value '" + value + "' must be <= " + str(max), primary_key_value=primary_key_value))
            

    def checkEnum(self, meta_attribute_definition:dict, meta_attribute_key:str, value:str, primary_key_value:str):
        # enumerated field check
        if (MetaUtils.exists(meta_attribute_definition, "Enum")):
            # enum is expected to be a list
            enum = meta_attribute_definition["Enum"]

            if (MetaUtils.exists(meta_attribute_definition, "Default")):
                if (value==meta_attribute_definition["Default"]):
                    # if trhe value equals the default then do nothing
                    return
           
            # check that the value exists within the provided list. If the value is blank then ignore it 
            # as we should have picked it up in the mandatory/optional test anyway
            # (i.e. if the field is optional but a value has been provided then we check it against the supplied list)
            if ( (len(value)>0) and (value not in enum) and (value != "(Null)") ):
                self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.METADATACOMPLIANCE.value, description="Error: Value '" + value + "' is outside the enumeration set '" + str(enum) + "'", primary_key_value=primary_key_value))



    def checkStartsWith(self, meta_attribute_definition:dict, meta_attribute_key:str, value:str, primary_key_value:str):
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
                    self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.FORMATCONSISTENCY.value, description="Error: Value '" + value + "' does not begin with any of: '" + str(startsWith) + "'", primary_key_value=primary_key_value))




            
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
                    self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.BUSINESSRULECOMPLIANCE.value, description="Error: Expression '" + ev + "' returned an error '" + str(e) + "'"))
                    result=None

                if ( (not result is None) and (result == False) ):
                    self.addDataQualityError(DataQualityError(meta_attribute_key,error_dimension=DataQualityDimension.BUSINESSRULECOMPLIANCE.value, description="Error: Expression '" + ev + "' returned FALSE"))

    