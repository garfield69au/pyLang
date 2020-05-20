import pyodbc
from prettytable import PrettyTable
from pyduq.langerror import ValidationError

class SQLTools(object):
    """
    SQLTools: This is a utility class to help manage SQL resultsets.
    Note: This could be replaced by Pandas
    """

    def __init__ (self, cursor):
        self.dataset = SQLTools.resultsetToDict(cursor)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if (self.dataset is None):
            raise ValidationError("DataSet is NULL.", None)
        
        pt = PrettyTable()
        row = next(iter(self.dataset.values())) # grab an arbritary row so we can lift the keys
        pt.field_names = row.keys()
        for i in self.dataset:
            # pull the fields out of the resultset row and add as discreet elements to print
            pt.add_row([field for field in self.dataset[field].values()])

        return str(pt)

    @staticmethod
    def resultsetToDict(cursor):
        """
        method resultsetToDict:
        Converts a SQL result set into a dictionary of lists keyed on the column name.
        """
        data = dict()

        # Get a list of the column names returned from the query
        columns = [column[0] for column in cursor.description]
     
        resultset = cursor.fetchall()
        colindex = 0
     
        for col in columns:
            data[col]= [("(Null)" if row[colindex] is None else str(row[colindex]).strip()) for row in resultset]            
            colindex += 1
        
        return data
    
    
    @staticmethod
    def getCol(dataset:dict, col:str) -> dict:
        """
        Slice a column out of the resultset based on col.
        The result is a dictionary of col and a list of values
        """
        return {col:SQLTools.getColValues(dataset, col)}
       

    @staticmethod
    def getColValues(dataset:dict, col:str) -> list:
        """
        Given a resultset and a column return all the values for that column as a list.
        """
        if (dataset is None):
            raise ValidationError("LANG Exception: DataSet has not been set", None)
   
        return dataset[col]


    @staticmethod
    def getColValuesAsDict(dataset:dict, *argv) -> dict:
        """
        Accepts an aribrtiary set of data columns as args and returns all the column values in a single dictionary.
        """
        if (dataset is None):
            raise ValidationError("LANG Exception: DataSet has not been set", None)

        if (argv is None):
            raise ValidationError("LANG Exception: argv has not been set", None)
        
        result = dict()
        
        for arg in argv:
            result[arg] = SQLTools.getColValues(dataset, arg)
            
        return result

    @staticmethod
    def rowCount(dataset:dict):
        """
        Return the count of rows in the resultset.
        """
        if (dataset is None):
            raise ValidationError("LANG Exception: DataSet has not been set", None)

        return len(dataset)
    
