import typing
import math
import statistics
import collections
from pyduq.metautils import MetaUtils
from scipy import stats
  
class DataProfile(object):
    """
    Profile: This class is used to profile a dataset and record various statistics about a set of data. The purpose of this class is to provide measurable
    values that can be used for explanation and comparison.

    """

    def __str__(self:object):
        return self.__repr__()
    
    def __repr__(self:object):
        return "[Profile: attribute: {0}, type: {1}, attribute_count: {2}, sum: {3} , mean: {4}, median: {5}, stddev: {6}, min_value: {7}, max_value: {8}, min_len: {9}, max_len: {10}]\n".format(self.attribute,self.type,self.attribute_count,self.sum, self.mean, self.median, self.stddev, self.min_val, self.max_val, self.min_len, self.max_len)

    def __init__(self:object):
        self.attribute=""
        self.type="<Unspecified>"
        self.count=0
        self.attribute_count=0
        self.position = 0
        self.sum = 0
        self.min_val = -1
        self.max_val = -1
        self.min_len = -1
        self.max_len = -1
        self.mean = 0
        self.variance = 0
        self.median = 0
        self.stddev = 0
        self.nullCount = 0
        self.blankCount = 0
        self.most_frequent_value = ""
        self.most_frequent_count = 0
        self.position = -1
        self.memory = 0
        self.pattern_count = 0
        self.patterns = ""
        self.defaultCount = 0
        self.defaultValue = ""


    def profileData(self, meta_attribute_definition:dict, colData:list, key:str):
        """
        For a given column, calculate a variety of statistics.
        """

        if (colData is None):
            raise ValidationError("LANG Exception: DataSet has not been set", None)
        
        if (meta_attribute_definition is None):
            raise ValidationError("LANG Exception: metadata has not been set", None)
        
        self.attribute = key
        if (MetaUtils.exists(meta_attribute_definition, "Type")):
            self.type = meta_attribute_definition["Type"]
        
        mode = stats.mode(colData)
        if (len(mode[0]) > 0):
            self.most_frequent_value = mode.mode[0]
            self.most_frequent_count = mode.count[0]
            
        vals = []
        self.count = len(colData)

        s=set(colData)
        s.discard("")
        self.patterns = str(sorted(s))
        self.patternCount = len(s)
        
        if (MetaUtils.exists(meta_attribute_definition, "Default")):
            self.defaultValue = meta_attribute_definition["Default"]
        
        if (len(self.defaultValue) == 0):
            self.defaultValue = "<Unspecified>"
            
        for value in colData:
            if ( (len(self.defaultValue) > 0) and (value == self.defaultValue) ):
                self.defaultCount += 1
                
            self.memory += len(value)
            val= math.nan

            if (len(value) < self.min_len or self.min_len == -1):
                self.min_len = len(value)
        
            if(len(value) > self.max_len or self.max_len == -1):
                self.max_len = len(value)
            
            if (value == "(Null)"):
                self.nullCount += 1
            elif (len(value) == 0):
                self.blankCount += 1
                    
            try:
                if (self.type in ["int","integer"]):
                    val = int(value)
                elif (self.type in ["float","number"]):
                    val = float(value)
                
                if (not math.isnan(val)):    
                    self.sum += val
                    vals.append(val)

                    if (val < self.min_val or self.min_val == -1):
                        self.min_val = val
                
                    if(val > self.max_val or self.max_val == -1):
                        self.max_val = val
                    
                self.attribute_count += 1
                
            except Exception as e:
                val=-1
        
        if (len(vals)>0):                  
            self.mean = statistics.mean(vals)                
            self.median = statistics.median(vals)
        
        if (len(vals)>=2):
            self.stddev = statistics.stdev(vals)
            self.variance = statistics.variance(vals)

                
    def setPosition(self, position:int):
        self.position = position
        
        
    def asDict(self):
        l = dict()
        l['attribute']= self.attribute
        l['position']= self.position
        l['type'] = self.type
        l['count'] = self.count
        l['attribute_count'] = self.attribute_count
        l['sum'] =self.sum
        l['mean'] =self.mean
        l['median'] =self.median
        l['stddev'] =self.stddev
        l['variance'] =self.variance
        l['min_value']= self.min_val
        l['max_value']=self.max_val
        l['min_len']= self.min_len
        l['max_len']=self.max_len
        l['null_count']=self.nullCount
        l['blank_count']=self.blankCount
        l['default_count']=self.defaultCount
        l['default_value']=self.defaultValue
        l['most_frequent_value']=self.most_frequent_value
        l['most_frequent_count']=self.most_frequent_count
        l['memory_consumed_bytes']=self.memory
        l['pattern_count']=self.patternCount
        l['patterns']=self.patterns
        return l
        