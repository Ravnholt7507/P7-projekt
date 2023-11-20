import models.traditionPredModels as traditionalModels
import models.AIPredModels as AIModels

def modelPicker(aisDataPoint):
        #if aisDataPoint[4]<10:
        return traditionalModels.pointBasedModel(aisDataPoint)
        #else:
                #return traditionalModels.COGBasedModel

#If COG is available