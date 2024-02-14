import commands2

from subsystems import *

class RunFeeder(commands2.Command):
    def __init__(self, launcher: Launcher):
        super().__init__
        self.launcher = launcher

    def initialize(self):
        self.launcher.run_feeder()
    
    def end(self, interrupted: bool):
        self.launcher.stop_feeder()

class RunFeederReversed(commands2.Command):
    def __init__(self, launcher: Launcher):
        super().__init__
        self.launcher = launcher

    def initialize(self):
        self.launcher.run_feeder(True)
    
    def end(self, interrupted: bool):
        self.launcher.stop_feeder()