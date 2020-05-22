import typing
import math
import statistics
import collections
from pyduq.metautils import MetaUtils
from scipy import stats
import string
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
stopwords = stopwords.words("english")

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
        self.csim=0.0

    
    def profile(self, metadata:dict, dataset:dict) ->list:
        if (metadata is None):
            raise ValidationError("LANG Exception: meta-data has not been set", None)
        elif (dataset is None):
            raise ValidationError("LANG Exception: resultset has not been set", None)
    
        profiles = []
        count = 1
        
        for meta_attribute_key in metadata.keys():
        
            # we can't presume that the meta data attribute exists in the dataset so we
            # check first.
            if (meta_attribute_key in dataset):
                profile = DataProfile().profileData(metadata[meta_attribute_key], dataset[meta_attribute_key], meta_attribute_key)
            else:
                profile = {}
                profile["attribute"] = meta_attribute_key
            
            profile["position"] = count
            count+= 1
            profiles.append(profile)
            
        return profiles


    def profileData(self, meta_attribute_definition:dict, colData:list, key:str) ->dict:
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

        if (self.type == "string"):
            cleaned = list(map(self.clean_string, colData))
            try:
                v = CountVectorizer().fit_transform(cleaned)
                vectors = v.toarray()
                self.csim = round(self.cosine_sim_vectors(vectors[0], vectors[1]), 3)
                
            except Exception as e:
                pass
        
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
        
        return self.to_dict()
    
    def cosine_sim_vectors(self, vec1, vec2) -> float:
        vec1 = vec1.reshape(1, -1)
        vec2 = vec2.reshape(1, -1)
        
        return cosine_similarity(vec1, vec2)[0][0]
        
    
    def clean_string(self:object, text):
        text = ''.join([word for word in text if word not in string.punctuation])
        text = text.lower()
        text = ' '.join([word for word in text.split() if word not in stopwords])
        
        return text
                
    def setPosition(self, position:int):
        self.position = position
        
        
    def to_dict(self):
        values = {}
        values['attribute']= self.attribute
        values['position']= self.position
        values['type'] = self.type
        values['count'] = self.count
        values['attribute_count'] = self.attribute_count
        values['sum'] =self.sum
        values['mean'] =self.mean
        values['median'] =self.median
        values['stddev'] =self.stddev
        values['variance'] =self.variance
        values['min_value']= self.min_val
        values['max_value']=self.max_val
        values['min_len']= self.min_len
        values['max_len']=self.max_len
        values['null_count']=self.nullCount
        values['blank_count']=self.blankCount
        values['default_count']=self.defaultCount
        values['default_value']=self.defaultValue
        values['most_frequent_value']=self.most_frequent_value
        values['most_frequent_count']=self.most_frequent_count
        values['csim']=self.csim
        values['memory_consumed_bytes']=self.memory
        values['pattern_count']=self.patternCount
        values['patterns']=self.patterns
        return values
        