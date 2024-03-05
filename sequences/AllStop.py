import commands2

from subsystems import Intake, Indexer, Launcher, Pivot, Elevator

class AllStop(commands2.Command):
    def __init__(self, intake:Intake, indexer:Indexer, launcher:Launcher, pivot:Pivot, elevator:Elevator):
        super().__init__()

        self.intake = intake
        self.indexer = indexer
        self.launcher = launcher
        self.pivot = pivot
        self.elevator = elevator

        self.addRequirements( intake, indexer, launcher, pivot, elevator )
        self.setName( "AllStop!" )

    def initialize(self):
        self.intake.stop()
        self.indexer.stop()
        self.launcher.stop()
        self.pivot.stop()
        self.elevator.stop()

    def isFinished(self): return True