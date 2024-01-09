import numpy as np
import copy

class BMSParser:
    def __init__(self):
        self.noteBars = []
        self.numOfBars = 0
        self.maxBeatOfNoteBars = 0
    
    def fileOpen(self,fileroute:str): # bms 파일을 연다
        self.bmsFile = open(fileroute, "rt", encoding='UTF-8')

    def offsetInit(self): # main data field 까지 파일 오프셋을 밀어버린다.
        self.bmsFile.seek(0)
        curTxt = self.bmsFile.readline()
        while(not curTxt.startswith("*---------------------- MAIN DATA FIELD")):
           curTxt = self.bmsFile.readline() 
        
    def readOneBar(self): # 한 마디를 파싱해서 읽는 함수 
        curTxt = self.bmsFile.readline() # 먼저 읽는다
        while(not curTxt.startswith("#") and not curTxt==""): # 레인 데이터를 찾을때 까지 readline
              curTxt = self.bmsFile.readline() 
        if(curTxt==""): return -1 # eof를 만나면 자동종료
    
        curBarNum = int(curTxt[1:4]) # 현재 어떤 마디의 데이터를 읽고 있는지 저장
        curBar = NoteBar(curBarNum) #현재 마디에 대한 자료구조를 생성한다.
        maxBeat = 0

        while(not curTxt.startswith("\n")): # 다음 마디로 넘어갈때까지 읽는다.(개행 넘어갈 때 까지)
            splittedTxt = curTxt.split(':') # : 를 기준으로 오브젝트 데이터를 나눈다.
            laneNum = NoteLane.setLaneNum(int(splittedTxt[0][4:])) #레인 넘버 데이터로 변환한다.
            if (laneNum == -1): # 노트에 대한 데이터가 아니면 파싱하지 않고 넘어간다. 
                curTxt = self.bmsFile.readline()
                continue
            nowLane = NoteLane(splittedTxt[1][:-1],laneNum)# 끝에오는 개행문자가 카운트 되지 않도록
            if(maxBeat < nowLane.beat ): maxBeat = nowLane.beat # 최대 비트그리드 수치를 찾음
            curBar.insertLane(nowLane)
            curTxt = self.bmsFile.readline()
        
        curBar.setMaxBeat(maxBeat)# max 비트 설정 

        for i in range(len(curBar.noteLaneSeq)): # 전체레인 퀀타이즈
            curBar.noteLaneSeq[i].quantize(maxBeat)
        
        self.noteBars.append(curBar) # 한 마디에 대해서 다읽었으면 마디 집합에 대해서 추가한다.
        self.numOfBars += 1
        if(self.maxBeatOfNoteBars < curBar.maximumBeat):
            self.maxBeatOfNoteBars = curBar.maximumBeat
        return 0 # 정상종료
    
    def readWholeBar(self): # 모든 마디를 다 읽어낸다. 
        while(self.readOneBar()==0):
            continue

    def to_numpy(self)->np.ndarray:
        tmp_bars = copy.deepcopy(self.noteBars)
        bar_list = []
        for bar in tmp_bars:
            lane_list = []
            for lane in bar.noteLaneSeq:
                if(bar.maximumBeat < self.maxBeatOfNoteBars):  # 넘파이 배열을 위해 Re-Quantize 
                    lane.quantize(self.maxBeatOfNoteBars)
                lane_list.append(lane.data)
            bar_list.append(lane_list)
        numpy_pattern = np.array(bar_list) 
        return numpy_pattern
    

    def fileClose(self):
        self.bmsFile.close()
        
                
                          
        
class NoteLane: # 한개의 레인을 저장하는 레인객체
    def __init__(self, noteSeq:str,laneNum:int):
        self.data = []
        for i in range(0, len(noteSeq),2):
            self.data.append(noteSeq[i:i+2])
        self.beat = len(noteSeq)//2
        self.laneNum = laneNum
        

    def quantize(self, targetBeat:int): #다른 레인과의 비트수를 맞춰주는 함수
        multiple = targetBeat//self.beat 
        if (multiple >= 1):
            newData = ["00"]*targetBeat
            for i in range(len(self.data)):
                newData[i*multiple] = self.data[i]
            self.beat = targetBeat
            self.data = newData
    
    @staticmethod
    def setLaneNum(laneNum:int): # 딕셔너리 이용해서, 레인 넘버를 맞춰주는 함수
        cases = {
            16:0, 11:1, 12:2, 13:3, 14:4, 15:5, 18:6, 19:7 
        }
        if(laneNum in cases): return cases[laneNum]
        else: return -1



class NoteBar:
    def __init__(self, barNum:int):
        self.barNum = barNum
        self.maximumBeat = 0 
        self.noteLaneSeq = [None]*8
        for i in range(8):
            self.noteLaneSeq[i] = NoteLane("00",i) # 디펄트로는 빈 노트레인을 생성
    def insertLane(self, lane:NoteLane):
        self.noteLaneSeq[lane.laneNum] = lane
    def setMaxBeat(self,maxBeat:int):
        self.maximumBeat = maxBeat
        
        

        
        

