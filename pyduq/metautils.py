
class MetaUtils(object):

    @staticmethod
    def exists(meta:dict, value:str) -> bool:
        return ( value in meta and not meta[value] is None )
    
    @staticmethod
    def isTrue(meta:dict, value:str) -> bool:
        return ( MetaUtils.exists(meta, value) and meta[value]==True )
        
    @staticmethod
    def isBlankOrNull(value:str) -> bool:
        return ( (len(value)==0) or (value == "(Null)") )

        
    @staticmethod
    def isAllowBlank(meta:dict) -> bool:
        return ( ("AllowBlank" in meta and not meta["AllowBlank"] is None) and (meta["AllowBlank"]==True) )
     
     
    @staticmethod    
    def isFloat(value) -> bool:
        try:
            float(value)
            return True
        except Exception as e:
            return False    
    
    @staticmethod
    def isInt(value) -> bool:
        try:
            int(value)
            return True
        except Exception as e:
            return False
            

        