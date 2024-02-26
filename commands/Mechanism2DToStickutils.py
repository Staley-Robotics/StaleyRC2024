from typing import Callable, Optional
import commands2
from commands2.subsystem import Subsystem
from wpiutil import SendableBuilder

from subsystems import Mechanism2DToStick

class wristToAngle(commands2.Command):
    def __init__(self, mech = Mechanism2DToStick()):
        super().__init__()
        self.mech = mech
        # self.time_pressed = 0 #by units of 1/50th a second
        
        #-----telemetry-----
        # self._inputX = inputX
        # self._inputY = inputY
        # print(f"self._inputX: {self._inputX}")
        # print(f"{self._inputY}")

    def initialize(self):
        self.mech.wristToAngle()
        # self.time_pressed = 0

        #-----telemetry
        # print("init worked for command scheduler")

    def execute(self):
        self.mech.wristToAngle()
        # self.time_pressed += 1
        # if self.time_pressed % 7 == 0 and self.time_pressed >= 20:
        #     self.mech.wristToAngle()

        #-----telemetry-----
        # print("_inputX:", self._inputX)
        # print("_inputY:", self._inputY)
        # print("execute worked for command scheduler")
    
    def isFinished(self) -> bool: return False

    def runsWhenDisabled(self) -> bool: return True
    
class updateMech(commands2.Command):
    def __init__(self, mech = Mechanism2DToStick()) -> None:
        super().__init__()
        self.mech = mech
    
    def initialize(self) -> None:
        self.mech.update()
        print("updateMech/initialize/complete")

    def execute(self) -> None:
        self.mech.update()
        print("updateMech/execute/executed")

    def isFinished(self) -> bool: return False

    def runsWhenDisabled(self) -> bool: return True