""" pyDUQMain.py

Overview
--------
pylang is a data quality validation tool that implements
the LANG data quality algorithms 
(see: Zhang, R., Indulska, M., & Sadiq, S. (2019). Discovering Data Quality Problems: The Case of Repurposed Data. 
Business and Information Systems Engineering, 61(5), 575–593. https://doi.org/10.1007/s12599-019-00608-0


USAGE
--------

$ python pylang -i <source_file_name> -m <meta_data_file_name> -o <outputfile_prefix> --profile --validate --custom <class_name> --infer

OUTPUT:
--------
The outout from pylang depends on what you want to achieve.
the --profile switch will trigger a data profile the source data 
and output the results as an Excel spreadsheet.

The --validate switch will trigger a validation of the source
data and the output will be a Spreadsheet of data quality
validation errors.

The --infer swutch will force the metadata to be inferred from the
data. (Note - if -v is used and there is no metadata provided then
--infer will be set).

The --profile switch generates a profile data file.


Change History:
-----------------
Version: 1.0    18/04/2020  Shane J. Downey
- Initial release


"""
#!/usr/bin/python

import sys
import os
import importlib
import argparse
import pyodbc
import time
from pyduq.AbstractDUQValidator import AbstractDUQValidator
from pyduq.SQLTools import SQLTools
from pyduq.duqvalidator import DUQValidator
from pyduq.patterns import Patterns
from pyduq.duqerror import ValidationError
from pyduq.filetools import FileTools
from pyduq.dataprofile import DataProfile


class pyDUQMain(object):

    def __init__(self):
        self.metadata = {}
        self.dataset = {}
    
    def loadSQL(self, URI:str, query:str):
        cnxn = pyodbc.connect(URI)
        cursor = cnxn.cursor()
        cursor.execute(query) 
        self.dataset = SQLTools(cursor).dataset
        print("SQL query returned " + str(len(self.dataset)) + " columns.")


    def loadMeta(self, metaFilename:str):
        self.metadata = FileTools.JSONtoMeta(metaFilename)        

    def inferMeta(self, outputFolder:str):
        stime = time.time()
        self.metadata = FileTools.inferMeta(self.dataset)
        FileTools.MetatoJSONFile("meta.json", self.metadata)
        print("Metadata file generated in " + str(time.time() - stime) + " secs")

    def loadCSV(self, inputFilename:str):
        self.dataset = FileTools.csvFileToDict(inputFilename)
        print("CSV file loaded " + str(len(self.dataset)) + " columns.")
    
    def loadXLS(self, inputFilename:str):
        self.dataset = FileTools.xlsFileToDict(inputFilename)
        print("Excel spreadsheet loaded " + str(len(self.dataset)) + " columns.")

    def validate(self, outputFolder:str, customValidator:str=""):
        try:
            stime = time.time()
     
            lang_validator = DUQValidator(self.dataset, self.metadata)
            lang_validator.validate()
            if ((not customValidator is None) and (len(customValidator) > 0)):
                lang_validator.counters.extend(self.customValidate(customValidator))

            lang_validator.saveCounters(outputFolder + "\\counters.xlsx")
            lang_validator.saveCountersSummary(outputFolder + "\\counters_summary.xlsx")
            
            print("Validation completed in " + str(time.time() - stime) + " secs")

        except ValidationError as e:
            print (e)


    def profile(self, outputFolder:str):
        try:
            stime = time.time()
            
            data_profile = DataProfile().profile(self.metadata, self.dataset)
            FileTools.saveProfile(outputFolder + "\\profile.xlsx", data_profile)
            
            print("Profile completed in " + str(time.time() - stime) + " secs")

        except ValidationError as e:
            print (e)

    
    def customValidate(self, full_class_string:str):        
        """
        dynamically load a class from a string in the format '<root folder>.<module filename>.<ClassName>'
        """
        class_data = full_class_string.split(".")
        module_path = ".".join(class_data[:-1])
        class_str = class_data[-1]

        try:            
            module = importlib.import_module(module_path)
        
            # Finally, we retrieve the Class
            custom_validator = getattr(module, class_str)
        except ImportError as e:
            raise(Exception("Unable to load: " + class_str + '\n'))
        
        if (not issubclass(custom_validator, AbstractDUQValidator)):
            raise(Exception("The custom validator '" + full_class_string + "' must inherit AbstractDUQValidator."))
        
        obj = custom_validator(self.dataset, self.metadata)
                
        obj.validate()

        return obj.counters
    
        
def main(argv):
    pl = pyDUQMain()
    inputFile = ""
    outputFolder = ""
    metaFile = ""
    sqlQuery = ""
    sqlURI = ""

    # Create the parser
    my_parser = argparse.ArgumentParser(description='Perform a data quality validation.')

    # Add the arguments
    my_parser.add_argument('-i',
                           '--ifile',
                           type=str,
                           help='the path and name of the input data file.')

    my_parser.add_argument('-o',
                           '--ofolder',
                           type=str,
                           help='the destination path for the output files to be stored.')
    
    my_parser.add_argument('-m',
                           '--mfile',
                           type=str,
                           help='the filename of the metadata-data file to use for validation.')
                           
    my_parser.add_argument('-s',
                           '--sql',
                           nargs=2,
                           type=str,
                           help='the database connection string and SQL query')
                           
    my_parser.add_argument('-c',
                           '--custom',
                           type=str,
                           help='The class path and name of a custom validator.')

    my_parser.add_argument('-p',
                           '--profile',
                           action="store_true",
                           help='profile the data.')

    my_parser.add_argument('-v',
                           '--validate',
                           action="store_true",
                           help='validate the data.')

    my_parser.add_argument('--infer',
                           action="store_true",
                           help='Generate metadata.')

    my_parser.add_argument('--verbose',
                           action="store_true",
                           help='Generate verbose output.')


    # Execute parse_args()
    args = my_parser.parse_args()

    inputFile = args.ifile
    metaFile = args.mfile
    outputFolder = args.ofolder
    profileFlag = args.profile
    validateFlag = args.validate
    inferFlag = args.infer
    __verbose__ = args.verbose
    customValidator = args.custom

    
    if ((not inputFile is None) and (len(inputFile)>0)):
        if not os.path.isfile(inputFile):
            print("The input file '" + inputFile + "' does not exist")
            sys.exit(1)
    else:
        if (args.sql is not None):
            sqlURI = args.sql[0]
            sqlQuery = args.sql[1]
        else:
            print("You must provide either an input file OR SQL connection and query. Run pyduqmain.py -h for help.")
            sys.exit(1)            
        
    if (len(sqlURI) >0 ):
        pl.loadSQL(sqlURI, sqlQuery)
    elif (len(inputFile)>0):
        if(inputFile.endswith(".csv")):
            pl.loadCSV(inputFile)
        elif(inputFile.endswith(".xlsx") or inputFile.endswith(".xltx")):
            pl.loadXLS(inputFile)
        else:
            print("Unsupported source data file type. Run pyduqmain.py -h for help.")
            sys.exit(1)            

    if (not metaFile is None):
        if (not os.path.isfile(metaFile)):
            print("The metadata-data file '" + metaFile + "' does not exist")
            sys.exit(1)
        pl.loadMeta(metaFile)
    else:
        if (not inferFlag):
            print("No metadata file was supplied - schema will be inferred from the dataset.")
        pl.inferMeta(outputFolder)

    if (validateFlag):
        pl.validate(outputFolder, customValidator)

    if (profileFlag):
        pl.profile(outputFolder)
        
    sys.exit(0)


if  __name__ =='__main__':
    main(sys.argv[1:])
