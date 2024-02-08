from typing import Callable, Optional
import commands2
from commands2.subsystem import Subsystem
from wpiutil import SendableBuilder

from subsystems import Mechanism2D

class IncrementWristAngle(commands2.Command):
    def __init__(self, mech = Mechanism2D()):
        super().__init__()
        self.mech = mech
        self.time_pressed = 0 #by units of 1/50th a second

    def initialize(self):
        self.mech.incrementWristAngle()
        self.time_pressed = 0
        print("IncrementWristAngle/initialize/Complete")

    def execute(self):
        self.time_pressed += 1
        if self.time_pressed % 7 == 0 and self.time_pressed >= 20:
            self.mech.incrementWristAngle()
        print("IncrementWristAngle/execute/happened")
    
    def isFinished(self) -> bool: return False

    def runsWhenDisabled(self) -> bool:
        return True

class DecrementWristAngle(commands2.Command):
    def __init__(self, mech = Mechanism2D):
        super().__init__()
        self.mech = mech
        self.time_pressed = 0 #by units of 1/50th a second

    def initialize(self):
        self.mech.decrementWristAngle()
        self.time_pressed = 0
        print("DecrementWristAngle/initialize/Complete")

    def execute(self):
        self.time_pressed += 1
        if self.time_pressed % 7 == 0 and self.time_pressed >= 25:
            self.mech.decrementWristAngle()
        print("DecrementWristAngle/execute/happened")
    
    def isFinished(self) -> bool: return False

    def runsWhenDisabled(self) -> bool:
        return True

class IncremementAngleIncrement(commands2.Command):
    def __init__(self, mech = Mechanism2D):
        super().__init__()
        self.mech = mech
        self.time_pressed = 0

    def initialize(self):
        self.mech.incrementAngleIncrement() 
        self.time_pressed = 0
    
    def execute(self):
        self.time_pressed += 1
        if self.time_pressed % 7 == 0 and self.time_pressed >= 25:
            self.mech.incrementAngleIncrement()

    def isFinished(self) -> bool: return False

    def runsWhenDisabled(self) -> bool:
        return True

class DecrementAngleIncrement(commands2.Command):
    def __init__(self, mech = Mechanism2D):
        super().__init__()
        self.mech = mech
        self.time_pressed = 0

    def initialize(self):
        self.mech.decrementAngleIncrement()
        self.time_pressed = 0
    
    def execute(self):
        self.time_pressed += 1
        if self.time_pressed % 7 == 0 and self.time_pressed >= 25:
            self.mech.decrementAngleIncrement()

    def isFinished(self) -> bool: return False

    def runsWhenDisabled(self) -> bool:
        return True