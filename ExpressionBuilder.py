import re

class ExpressionBuilder(object):
 
    def parseExpr(self, expr:str): 
        re.purge()
        return(re.findall(r"[^[]*\[([^]]*)\]", expr))
 
    def stripBrackets(self, str):
        result=str
        
        # find the brackets and remove them from the string
        for c in ["[","]"]:
            result=result.replace(c,"")
            
        return result
    
    def merge(self, expr, d:dict):
        s=self.stripBrackets(expr)
        for k,v in d.items():
            s=s.replace(k, str(v))
            
        return s
        
    def charPosition(string:str, c):
        pos = [] #list to store positions for each 'char' in 'string'
        for n in range(len(string)):
            if string[n] == char:
                pos.append(n)
        
        return pos

        
    def multiReplace(string, replacements, ignore_case=False):
        """
        Given a string and a dict, replaces occurrences of the dict keys found in the 
        string, with their corresponding values. The replacements will occur in "one pass", 
        i.e. there should be no clashes.
        :param str string: string to perform replacements on
        :param dict replacements: replacement dictionary {str_to_find: str_to_replace_with}
        :param bool ignore_case: whether to ignore case when looking for matches
        :rtype: str the replaced string
        """
        if (ignore_case):
            replacements = dict((pair[0].lower(), pair[1]) for pair in sorted(replacements.iteritems()))

        rep_sorted = sorted(replacements, key=lambda s: (len(s), s), reverse=True)
        rep_escaped = [re.escape(replacement) for replacement in rep_sorted]
        pattern = re.compile("|".join(rep_escaped), re.I if ignore_case else 0)
        
        return pattern.sub(lambda match: replacements[match.group(0).lower() if ignore_case else match.group(0)], string)
        
        