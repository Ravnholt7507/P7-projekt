class shoreReciever:
    def __init__(self, pointBasedSOGLimit, models) -> None:
        self.pointBasedSOGlimit = pointBasedSOGLimit
        self.models = models

def DetPredParam(SOG, COG, shoreReciever):
    if SOG <= shoreReciever.pointBasedSOGLimit:
        return shoreReciever.models.pointBased
