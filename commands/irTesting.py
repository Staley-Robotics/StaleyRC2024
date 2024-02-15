import wpilib

from commands2 import Command

import logging

class EnableEmitter(Command):
    def __init__(self, emitter:wpilib.DigitalOutput):
        super().__init__()
        self.emitter = emitter
    
    def initialize(self):
        self.emitter.set(True)
    
    def isFinished(self) -> bool:
        return True

class DisableEmitter(Command):
    def __init__(self, emitter:wpilib.DigitalOutput):
        super().__init__()
        self.emitter = emitter
    
    def initialize(self):
        self.emitter.set(False)
    
    def isFinished(self) -> bool:
        return True
    
class printReciever(Command):
    def __init__(self, reciever: wpilib.DigitalInput):
        super().__init__()
        self.reciever = reciever
    
    def run(self):
        #print(self.reciever.get())
        #logging.log(1, self.reciever.get())
        wpilib.SmartDashboard.putBoolean('ir recieving', self.reciever.get())
    
    def end(self, interrupted: bool):
        return super().end(interrupted)
    