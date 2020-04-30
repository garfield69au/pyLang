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
        Converts a SQL result set into a dictionary of dictionaries.
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

        # Get a list of the column names returned from the query
        columns = [column[0] for column in cursor.description]
        rowindex=1

        dataset = cursor.fetchall()
     
        for row in dataset:
            colindex = 0
        
            l = dict()
           
            for col in columns:
                """
                It's important to note that Nulls are converted to "(Null)" so that routines that compare items
                (like list.sort() don't break).
                """
               
                l[col] = ("(Null)" if row[colindex] is None else str(row[colindex]).strip().lstrip("0"))
                colindex += 1
 
            data[rowindex]=l
            rowindex+=1
            
        return data
    
    
    @staticmethod
    def getCol(dataset:dict, col:str) -> dict:
        """
        Slice a column out of the resultset based on col.
        The result is a dictionary of col and a list of values
        """
        result=dict()    
        result[col]=SQLTools.getColValues(dataset, col)
        return result
       

    @staticmethod
    def getColValues(dataset:dict, col:str) -> list:
        """
        Given a resultset and a column return all the values for that column as a list.
        """
        if (dataset is None):
            raise ValidationError("LANG Exception: DataSet has not been set", None)

        vals=list()

        for rowindex in dataset:
            if (not col in dataset[rowindex].keys()):
                raise ValidationError("LANG Error: The metadata column '" + col + "' not found in the dataset.",None)
            else:
                vals.append(dataset[rowindex].get(col))
        return vals


    @staticmethod
    def getColValuesAsDict(dataset:dict, *argv) -> dict:
        """
        Accepts an aribrtiary set of data columns as args and returns all the column values in a single dictionary.
        """
        if (dataset is None):
            raise ValidationError("LANG Exception: DataSet has not been set", None)

        if (argv is None):
            raise ValidationError("LANG Exception: argv has not been set", None)

        vals=dict()
        for arg in argv:
            vals[arg] = SQLTools.getColValues(dataset, arg)
            
        return vals
        

    @staticmethod
    def rowCount(dataset:dict):
        """
        Return the count of rows in the resultset.
        """
        if (dataset is None):
            raise ValidationError("LANG Exception: DataSet has not been set", None)

        return len(dataset)
    
