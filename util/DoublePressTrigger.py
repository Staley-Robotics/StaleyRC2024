from enum import Enum, auto
from wpilib import Timer
from commands2.button import Trigger

class DoublePressState(Enum):
    IDLE = auto()
    FIRST_PRESS = auto()
    FIRST_RELEASE = auto()
    SECOND_PRESS = auto()

class DoublePressTrigger:
    maxLengthSecs:float = 0.4
    trigger:Trigger = None
    resetTimer:Timer = Timer()
    state:DoublePressState = DoublePressState.IDLE

    @staticmethod
    def doublePress( baseTrigger:Trigger ):
        myTrigger = DoublePressTrigger( baseTrigger )
        return Trigger( myTrigger.get )

    def __init__(self, baseTrigger:Trigger):
        self.trigger = baseTrigger

    def get(self) -> bool:
        pressed:bool = self.trigger.getAsBoolean()
        match self.state:
            case DoublePressState.IDLE:
                if pressed:
                    self.state = DoublePressState.FIRST_PRESS
                    self.resetTimer.reset()
                    self.resetTimer.start()
            case DoublePressState.FIRST_PRESS:
                if not pressed:
                    if self.resetTimer.hasElapsed( self.maxLengthSecs ):
                        self.reset()
                    else:
                        self.state = DoublePressState.FIRST_RELEASE
            case DoublePressState.FIRST_RELEASE:
                if pressed:
                    self.state = DoublePressState.SECOND_PRESS
                elif self.resetTimer.hasElapsed( self.maxLengthSecs ):
                    self.reset()
            case DoublePressState.SECOND_PRESS:
                if pressed: self.reset()
        return self.state == DoublePressState.SECOND_PRESS
    
    def reset(self) -> None:
        self.state = DoublePressState.IDLE
        self.resetTimer.stop()
