from wpilib import RobotState
from commands2 import Subsystem

from .ElevatorIO import ElevatorIO
from util import *

class Elevator(Subsystem):
    class ElevatorPositions:
        Bottom = NTTunableFloat( "/Config/ElevatorPositions/Bottom", 0.0, persistent=True )
        Amp = NTTunableFloat( "/Config/ElevatorPositions/Amp", 0.0, persistent=True )
        Source = NTTunableFloat( "/Config/ElevatorPositions/Source", 0.0, persistent=True )
        Climb = NTTunableFloat( "/Config/ElevatorPositions/Climb", 0.0, persistent=True )
        Trap = NTTunableFloat( "/Config/ElevatorPositions/Trap", 0.0, persistent=True )
        Top = NTTunableFloat( "/Config/ElevatorPositions/Top", 0.0, persistent=True )

    def __init__(self, elevator:ElevatorIO):
        self.elevator = elevator
        self.elevatorInputs = elevator.ElevatorIOInputs
        self.elevatorLogger = NetworkTableInstance.getDefault().getStructTopic( "/Elevator", ElevatorIO.ElevatorIOInputs ).publish()
        self.pivotMeasuredLogger = NetworkTableInstance.getDefault().getTable("/Logging/Elevator")
        
        self.offline = NTTunableBoolean( "/DisableSubsystem/Elevator", False, persistent=True )

    def periodic(self):
        # Logging
        self.elevator.updateInputs( self.elevatorInputs )
        self.elevatorLogger.set( self.elevatorInputs )

        # Run Subsystem
        if RobotState.isDisabled() or self.offline.get():
            self.stop()

        if False: #self.isCharacterizing.get():
            self.pivot.runCharacterization( self.charSettingsVolts.get(), self.charSettingsRotation.get() )
        else:
            self.elevator.run()
            # self.pivot.pivotMotor.set(0)

        # Post Run Logging
        self.pivotMeasuredLogger.putNumber( "Setpoint", self.elevator.getSetpoint() )
        self.pivotMeasuredLogger.putNumber( "Measured", self.elevator.getPosition() )

    def set(self, position) -> None:
        self.elevator.setPosition( min( max( position, Elevator.ElevatorPositions.Bottom.get() ), Elevator.ElevatorPositions.Top.get() ) )

    def stop(self) -> None:
        self.set( self.elevator.getPosition() )

    def movePosition(self, position) -> None: pass

    def atPosition(self) -> bool: return True