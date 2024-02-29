### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command

# Our Imports
from subsystems import Elevator
from util import *

# Intake Load Command
class ElevatorTop(Command):
    def __init__( self,
                  elevator:Elevator,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.elevator = elevator

        self.setName( "ElevatorTop" )
        self.addRequirements( elevator )

    def initialize(self) -> None: pass

    def execute(self) -> None:
        self.elevator.set(Elevator.ElevatorPositions.Top.get())

    def end(self, interrupted:bool) -> None:
        pass # May be set to zero in future, but for now: assuming hold position

    def isFinished(self) -> bool:
        return self.elevator.atPosition()
    
    def runsWhenDisabled(self) -> bool: return False
