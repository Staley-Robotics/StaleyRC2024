### Imports
# Python Imports
# None

# FRC Component Imports
from commands2 import Command
from wpilib import Timer

# Our Imports
from subsystems import Intake

# Intake Load Command
class IntakeStop(Command):
    def __init__( self,
                  intake:Intake,
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.intake = intake
        
        self.setName( "IntakeStop" )
        self.addRequirements( intake )

    def initialize(self) -> None:
        self.intake.setBrake(False)
        self.intake.stop()

    def execute(self) -> None:
        pass

    def end(self, interrupted:bool) -> None:
        pass

    def isFinished(self) -> bool:
        return True
    
    def runsWhenDisabled(self) -> bool: return False