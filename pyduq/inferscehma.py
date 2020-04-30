from pyduq.dataprofile import DataProfile

class InferSchema(object):

    @sttaicmethod
    def generate(rs: dict) -> dict:
        meta = dict()

        keys = rs.keys()

        for key in keys:
            colData = SQLTools.getCol(rs, key)
            if ( (not colData is None) and (len(colData[meta]) > 0) ):
                profile = InferSchema.profileData(colData, "")
                profile.setPosition(len(meta)+1)
                meta[key] = profile
                
        return meta
        
   
    @sttaicmethod    
    def profileData(colData:dict, key:str) ->dict:
        profile = DataProfile()
        profile.profileData(colData, key)
        
        return profile.asDict()
        