"""
piLANG.py

Overview
--------
piLANG is a data quality validation tool that implements
the LANG data quality algorithms 
(see: Zhang, R., Indulska, M., & Sadiq, S. (2019). Discovering Data Quality Problems: The Case of Repurposed Data. Business and Information Systems Engineering, 61(5), 575–593. https://doi.org/10.1007/s12599-019-00608-0


USAGE
--------

$ python piLANG -i <source_file_name> -m <meta_data_file_name> -o <outputfile_prefix> --profile --validate --custom <class_name>

OUTPUT:
--------
The outout from piLANG depends on what you want to achieve.
the --profile switch will trigger a data profile the source data 
and output the results as an Excel spreadsheet.

The --validate switch will trigger a validation of the source
data and the output will be a Spreadsheet of data quality
validation errors.



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
from piLang.piLang.SQLTools import SQLTools
from piLang.piLang.AbstractLangValidator import AbstractLangValidator
from piLang.piLang.LangValidator import LangValidator, PatternFormat
from piLang.piLang.LangError import ValidationError
from piLang.piLang.AbstractLangValidator import PatternFormat
from piLang.piLang.FileTools import FileTools
import time

class piLANG(object):
    
    def loadSQL(self, URI:str, query:str):
        cnxn = pyodbc.connect(URI)
        cursor = cnxn.cursor()
        cursor.execute(query) 
        self.dataset = SQLTools(cursor).rs

    def loadMeta(self, metaFilename:str):
        self.meta = FileTools.JSONtoMeta(metaFilename)        

    def loadCSV(self, inputFilename:str):
        self.dataset = FileTools.csvFileToDict(inputFilename)
    
    def validate(self, inputFilename:str, outputFolder:str):
        try:
            stime = time.time()
     
            lang_validator = LangValidator(self.dataset, self.meta)
            lang_validator.validate()
            lang_validator.saveCounters(outputFolder + "counters.xlsx")
            lang_validator.saveProfile(outputFolder + "profile.xlsx")
            
            print("Completed in " + str(time.time() - stime) + " secs")

        except ValidationError as e:
            print (e)

    def profile(self, inputFilename:str, outputFilename:str):
        pass
    
    def customValidate(self, full_class_string:str):        
        """
        dynamically load a class from a string
        """

        class_data = full_class_string.split(".")
        module_path = ".".join(class_data[:-1])
        class_str = class_data[-1]

        try:            
            module = importlib.import_module(module_path)
        
            # Finally, we retrieve the Class
            custom_validator = getattr(module, class_str)
        except ImportError as e:
            print("Unable to load: " + class_str + '\n')
            print(e)
            return
        
        rs = dict()
        meta = dict()

        if (not issubclass(custom_validator, AbstractLangValidator)):
            raise(Exception("The custom validator '" + full_class_string + "' must inherit AbstractLangValidator."))
        
        obj = custom_validator(rs, meta)
                
        obj.validate()
        print(obj.counters)
    
        
def main(argv):
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
                           required=True,
                           help='the path and name of the input data file.')

    my_parser.add_argument('-o',
                           '--ofolder',
                           type=str,
                           help='the destination path for the output files to be stored.')
    
    my_parser.add_argument('-m',
                           '--mfile',
                           type=str,
                           help='the filename of the meta-data file to use for validation.')
                           
    my_parser.add_argument('-s',
                           '--sql',
                           nargs=2,
                           type=str,
                           help='the filename of the meta-data file to use for validation.')
                           

    my_parser.add_argument('-p',
                           '--profile',
                           action="store_true",
                           help='profile the data.')

    my_parser.add_argument('-v',
                           '--validate',
                           action="store_true",
                           help='validate the data.')

    # Execute parse_args()
    args = my_parser.parse_args()

    inputFile = args.ifile
    metaFile = args.mfile
    outputFolder = args.ofolder
    profileFlag = args.profile
    validateFlag = args.validate
    
    if (not args.sql is None):
        if (len(args.sql) != 2) :
            print("In order to run a SQL query you must provide the connection string followed by the SQL query.")
            sys.exit()
        
        sqlURI = args.sql[0]
        sqlQuery = args.sql[1]
        
    if not os.path.isfile(inputFile):
        print('The file specified does not exist')
        sys.exit()

    pl = piLANG()
    
    #if (validateFlag):
    pl.loadMeta(metaFile)
    pl.loadSQL(sqlURI, sqlQuery)
    pl.validate(inputFile, outputFolder)
    
    if (profileFlag):
        pass
        
    #piLANG.customValidate(r'validator.MotherDetailValidator.MotherDetailValidator')
    
    sys.exit()


if  __name__ =='__main__':
    main(sys.argv[1:])