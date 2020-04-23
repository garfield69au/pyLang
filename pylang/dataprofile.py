import typing
import math
import statistics
import collections
from pylang.pylang.validator import Validator
  
class DataProfile(object):
    """
    Profile: This class is used to profile a dataset and record various statistics about a set of data. The purpose of this class is to provide measurable
    values that can be used for explanation and comparison.

    """

    def __str__(self:object):
        return self.__repr__()
    
    def __repr__(self:object):
        return "[Profile: attribute: {0}, type: {1}, attribute_count: {2}, sum: {3} , mean: {4}, median: {5}, stddev: {6}, min_value: {7}, max_value: {8}, min_len: {9}, max_len: {10}]\n".format(self.attribute,self.type,self.attributeCount,self.sum, self.mean, self.median, self.stddev, self.min_val, self.max_val, self.min_len, self.max_len)

    def __init__(self:object):
        self.attribute=""
        self.type="<Unspecified>"
        self.count=0
        self.attributeCount=0
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
        self.distinctVals = 0
        self.mostFrequent = ""
        self.position = -1
        self.memory = 0


    def profileData(self, meta:dict, colData:dict, key:str):
        """
        For a given column, calculate a variety of statistics.
        """
        
        self.attribute = key
        if (Validator.exists(meta, "Type")):
            self.type = meta["Type"]
        
        self.distinctVals = len(set(colData))
        self.mostFrequent = max(set(colData), key=colData.count)
        
        vals = list()
        self.count = len(colData)
        
        for value in colData:    
            
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
                if (self.type=="int"):
                    val = int(value)
                elif (self.type=="float"):
                    val = float(value)
                
                if (not math.isnan(val)):    
                    self.sum += val
                    vals.append(val)

                    if (val < self.min_val or self.min_val == -1):
                        self.min_val = val
                
                    if(val > self.max_val or self.max_val == -1):
                        self.max_val = val
                    
                self.attributeCount += 1
                
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
        
    def values(self):
        l = list()
        l.append(self.attribute)
        l.append(self.position)
        l.append(self.type)
        l.append(self.count)
        l.append(self.attributeCount)
        l.append(self.sum)
        l.append(self.mean)
        l.append(self.median)
        l.append(self.stddev)
        l.append(self.variance)
        l.append(self.min_val)
        l.append(self.max_val)
        l.append(self.min_len)
        l.append(self.max_len)
        l.append(self.nullCount)
        l.append(self.blankCount)
        l.append(self.distinctVals)
        l.append(self.mostFrequent)
        l.append(self.memory)
        return l
    
    def keys(self):
        l = list()
        l.append('attribute')
        l.append('position')
        l.append('type')
        l.append('count')
        l.append('attribute_count')
        l.append('sum')
        l.append('mean')
        l.append('median')
        l.append('stddev')
        l.append('variance')
        l.append('min_value')
        l.append('max_value')
        l.append('min_len')
        l.append('max_len')
        l.append('null_count')
        l.append('blank_count')
        l.append('distinct_values')
        l.append('most_frequent_value')
        l.append('memory_consumed_bytes')
        return l
    
    def asDict(self):
        l = dict()
        l['attribute']= self.attribute
        l['position']= self.position
        l['type'] = self.type
        l['count'] = self.count
        l['attribute_count'] = self.attributeCount
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
        l['distinct_values']=self.distinctVals
        l['most_frequent_value']=self.mostFrequent
        l['memory_consumed_bytes']=self.memory
        return l
        
