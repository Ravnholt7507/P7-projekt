import models.traditionPredModels as traditionalModels
import models.AIPredModels as AIModels

def modelPicker(aisDataPoint):
        #if aisDataPoint[4]<10:
        print("MODELPICKER: Choosing model")
        print("MODELPICKER: Choosing COGBasedModel")
        return traditionalModels.COGBasedModel(aisDataPoint)
        #else:
                #return traditionalModels.COGBasedModel

#If COG is available