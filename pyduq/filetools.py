import csv
import json
from prettytable import PrettyTable
import dicttoxml
from xml.dom.minidom import parseString
from pyduq.langerror import ValidationError
from unidecode import unidecode

class FileTools(object):
    """
    FileTools: This is a utility class to help manage data files.
    The file is expected to be in a CSV format with a header row.
    Note: This could be replaced by Pandas
    """

    @staticmethod
    def csvFileToDict(fileName:str):
        """ csvFileToDict:
        Converts a csv file into a dictionary of dictionaries.
        Each row is its own dictionary with each attribute recorded as a tupple,
        indexed by a row counter.
        """
        data = dict()
        resultset = list()
        
        # first we load the data into a simple 
        with open(fileName, errors='ignore') as f:
            reader = csv.DictReader(f)
                               
            # Get a list of the column names returned from the file
            columns = list(reader.fieldnames)
            
            for row in reader:
                resultset.append(row)
                
            for col in columns:
                data[col]= [("(Null)" if row[col] is None else FileTools.FormatString(str(row[col]).strip())) for row in resultset]            
        
        return data
  
    @staticmethod
    def JSONtoMeta(fileName:str):
        meta = dict()
        
        with open(fileName, 'r', errors='ignore') as json_file:
            meta = json.load(json_file)
          
        return meta
  
    @staticmethod
    def MetatoXMLFile(xml_filename:str, meta:dict):
        xml = dicttoxml.dicttoxml(meta)
        dom = parseString(xml)

        with open(xml_filename, 'w') as w:
            w.write(dom.toprettyxml())
            
    @staticmethod
    def MetatoJSONFile(JSON_filename:str, meta:dict):
        json_dict = json.dumps(meta, indent=4)
        
        with open(JSON_filename, 'w') as w:
            w.write(json_dict)
            
    
    @staticmethod
    def FormatString(s:str) ->str:
        # converts a unicode string to ascii
        
        if isinstance(s, str):
            try:
                s.encode('ascii')
                return s
            except:
                return unidecode(s)
        else:
          return s
