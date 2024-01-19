from typing import Callable, Optional
import commands2
from commands2.subsystem import Subsystem
from wpiutil import SendableBuilder

from subsystems import Launcher

'''class IncrementLauncherSpeed(commands2.InstantCommand):
    def __init__(self, launcher: Launcher):
        super().__init__(toRun = lambda : launcher.increment_speed())
    def runsWhenDisabled(self) -> bool: return True
class DecrementLauncherSpeed(commands2.InstantCommand):
    def __init__(self, launcher: Launcher):
        super().__init__(toRun = lambda : launcher.decrement_speed())
    def runsWhenDisabled(self) -> bool: return True'''

class IncrementLauncherSpeed(commands2.Command):
    def __init__(self, launcher: Launcher):
        super().__init__()
        self.launcher = launcher
        self.time_pressed = 0 #by units of 1/50th a second

    def initialize(self):
        self.launcher.increment_speed()
        self.time_pressed = 0

    def execute(self):
        self.time_pressed += 1
        if self.time_pressed % 7 == 0 and self.time_pressed >= 20:
            self.launcher.increment_speed()
    
    def isFinished(self) -> bool: return False

class DecrementLauncherSpeed(commands2.Command):
    def __init__(self, launcher: Launcher):
        super().__init__()
        self.launcher = launcher
        self.time_pressed = 0 #by units of 1/50th a second

    def initialize(self):
        self.launcher.decrement_speed()
        self.time_pressed = 0

    def execute(self):
        self.time_pressed += 1
        if self.time_pressed % 7 == 0 and self.time_pressed >= 25:
            self.launcher.decrement_speed()
    
    def isFinished(self) -> bool: return False


