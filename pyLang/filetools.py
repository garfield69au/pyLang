import csv
import json
from prettytable import PrettyTable
import dicttoxml
from xml.dom.minidom import parseString
from pyLang.pyLang.langerror import ValidationError

class FileTools(object):
    """
    FileTools: This is a utility class to help manage data files.
    The file is expected to be in a CSV format with a header row.
    Note: This could be replaced by Pandas
    """

    @staticmethod
    def csvFileToDict(fileName:str):
        """
        method csvToDict:
        Converts a csv file into a dictionary of dictionaries.
        Each row is its own dictionary with each attribute recorded as a tupple,
        indexed by a row counter.
        e.g.
        {
            0: {'col1': 1, 'col2': None},
            1: {'col1': 1, 'col2': ""},
            2: {'col1': 1, 'col2': 1}
        }
        """
        data = dict()
        
        # first we load the data into a simple 
        with open(fileName) as f:
            reader = csv.DictReader(f)
                               
            # Get a list of the column names returned from the file
            columns = list(reader.fieldnames)
 
            rowindex=1

            for row in reader:                        
                l = dict()
               
                for col in columns:
                    """
                    It's important to note that Nulls are converted to "(Null)" so that routines that compare items
                    (like list.sort() don't break).
                    """
            
                    l[col] = ("(Null)" if row[col] is None else str(row[col]).strip().lstrip("0"))
     
                data[rowindex]=l
                rowindex+=1
                
        return data
  
    @staticmethod
    def JSONtoMeta(fileName:str):
        meta = dict()
        
        with open(fileName, 'r') as json_file:
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
            
            