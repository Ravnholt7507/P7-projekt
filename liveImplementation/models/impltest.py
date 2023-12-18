import settings as s
import main as main


for dit in s.timeInterval:
    s.timeInterval = dit
    for dat in s.radiusSeq:
        s.radius = dat
        for dut in s.rateOfTurnSeq:
            s.rateOfTurn = dut
            main.main()
    
