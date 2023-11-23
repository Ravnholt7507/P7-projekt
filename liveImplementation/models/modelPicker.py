import models.traditionPredModels as traditionalModels
import models.AIPredModels as AIModels

def modelPicker(aisDataPoint):
        if aisDataPoint['SOG'] * 1.852 < 10:
                return traditionalModels.pointBasedModel(aisDataPoint)
        else:
                return traditionalModels.COGBasedModel(aisDataPoint)
