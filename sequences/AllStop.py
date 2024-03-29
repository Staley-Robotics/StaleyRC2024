import commands2

from subsystems import Intake, Indexer, Launcher, Pivot

class AllStop(commands2.Command):
    def __init__(self, intake:Intake, indexer:Indexer, launcher:Launcher, pivot:Pivot):
        super().__init__()

        self.intake = intake
        self.indexer = indexer
        self.launcher = launcher
        self.pivot = pivot

        self.addRequirements( intake, indexer, launcher, pivot )
        self.setName( "AllStop!" )

    def initialize(self):
        self.intake.stop()
        self.indexer.stop()
        self.launcher.stop()
        self.pivot.stop()

    def isFinished(self): return False