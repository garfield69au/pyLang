import string
import re
import operator
from piLang.piLang.SQLTools import SQLTools
from prettytable import PrettyTable
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords, nps_chat
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
import nltk

class MatchResult(object):
    
    def __init__(self:object, score:float, code:str, tokens:list):
        self.score = score
        self.code = code
        self.tokens = tokens
        
        
    def __repr__(self):
        return self.__str__()
 
    def __str__(self):
        x=""
        for s in self.tokens:
            x =x + s + " "
        return "Code: {0}, Score: {1}, Tokens: {2}\n".format(self.code, self.score, x)

        
class ICD10TextSearch(object):
    """
    ICD10TextSearch: Provodes a class for searching ICD10 code tables. It requires a dictionary of codes and descriptions and
    a search string written in natural language.
    This class uses the NLTK natural language tool kit.
    """
    
    def __init__(self:object, rs:dict):
        """
        Creates a set of stop words - these will be filtered out of the search string 
        """
        self.code_set=dict()
        self.stop_words=set(stopwords.words("english"))
        self.stop_words.add("unspecified")
        self.stop_words.add("cardiologist")
        self.ps = PorterStemmer()
        self.wnl = WordNetLemmatizer()
        
        for key in rs:
            row=rs[key]
            code = row["code"]
            descr = row["description"]                 
            tokens = self.tokenize(descr)
            if (len(tokens)>0):
                self.code_set[code]=tokens

            
    def search(self:object, searchstr:str) -> dict:           
        match_list=list()
        search_tokens = self.tokenize(searchstr)
        
        if (len(search_tokens) > 0):
            for key in self.code_set:
                row = self.code_set[key]
                try:
                    match_score=round(nltk.jaccard_distance(set(search_tokens), set(row)), 3)
                    if (match_score < 1.0):
                        match_list.append(MatchResult(match_score, key, row))    
                except Exception as e:
                    print(str(e) + ", " + searchstr + ", " + str(search_tokens))
                    
            match_list.sort(key=operator.attrgetter('score'))
        
        return match_list

    def match(self:object, searchstr:str) -> str:   
        match_list = self.search(searchstr)        

        s="0"
        if (match_list):
            match_list.sort(key=operator.attrgetter('score'))
            s=match_list[0]
        return s
        
        
    def tokenize(self:object, text:str):
        tokenized_text = word_tokenize(text.strip().lower())
        cleaned_text = [self.ps.stem(t) for t in tokenized_text if t not in self.stop_words and re.match('[a-zA-Z\-][a-zA-Z\-]{2,}', t)]
        cleaned_text = [self.wnl.lemmatize(t,'v') for t in cleaned_text if t not in self.stop_words]
        return cleaned_text
