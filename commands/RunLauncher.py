import commands2

from subsystems import *

class RunLauncher(commands2.Command):
    def __init__(self, launcher: Launcher):
        super().__init__()
        self.launcher = launcher

    def initialize(self):
        self.launcher.start_launcher()
    
    def end(self, interrupted: bool):
        self.launcher.stop_launcher()
    
    def isFinished(self) -> bool:
        return False