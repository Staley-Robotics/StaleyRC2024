from hal import *
from ntcore import NetworkTableInstance
from wpilib import RobotBase

#from subsystems import *

class Logger:
    tables = {}
    isReplay = False

    @staticmethod
    def getInstance():
        if loggerInstance == None:
            loggerInstance = Logger()
        return loggerInstance

    def __init__(self):
        pass

    def setReplay(self, replay:bool):
        self.isReplay = replay

    def createNTPublisher(self, key:str, type:any ):
        tbl = NetworkTableInstance.getDefault().getStructTopic( f"/{key}", type ).publish()
        self.tables.update( { key: tbl } )
        return tbl

    def processInputs( self, key, data ):
        pub:StructPublisher = self.tables.get(key)
        if pub == None:
            pub = self.createNTPublisher( key, type(data) )

        pub.set( data )

    def recordOutputs( self, key, data ):
        base = "/RealOutputs/"
        if RobotBase.isSimulation() and self.isReplay:
            base = "/ReplayOutputs/"

    @staticmethod
    def getRealTimestamp():
        return 0
    
    @staticmethod
    def periodicBeforeUser():
        pass

    @staticmethod
    def periodicAfterUser(start, end):
        pass

loggerInstance = None