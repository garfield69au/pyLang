
class MetaUtils(object):
    """ MetaUtils: 
    This is a helper class for processing metadata attributes. 
    At some stage we might create a metadata class, in which case
    these methods would be rolled into that class.
    """
    
    @staticmethod
    def exists(meta:dict, value:str) -> bool:
        return ( (value in meta) and (not meta[value] is None) )
    
    @staticmethod
    def isTrue(meta:dict, value:str) -> bool:
        return ( (MetaUtils.exists(meta, value)) and (meta[value]==True) )
        
    @staticmethod
    def isBlankOrNull(value:str) -> bool:
        return ( (len(value)==0) or (value == "(Null)") )

    @staticmethod
    def isAllowBlank(meta:dict) -> bool:
        return ( MetaUtils.isTrue(meta, "AllowBlank") )
     
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
