import BMSparser as bp

parser = bp.BMSParser()
parser.fileOpen("your_own_bms_file")
parser.offsetInit()
parser.readWholeBar()
parser.fileClose()

for bar in parser.noteBars:
    for lane in bar.noteLaneSeq:
       for data in lane.data:
           print(data, end=" ")
       print()
    print()
        
            