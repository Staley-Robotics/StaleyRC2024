from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import DriverStation

from util import *
from .ClimberIO import ClimberIO

class Climber(Subsystem):
    class ClimberPositions:
        Bottom = NTTunableFloat( "/Config/ClimberPositions/Bottom", 0.0, persistent=True )
        Top = NTTunableFloat( "/Config/ClimberPositions/Top", 50.0, persistent=True )
        Reset = NTTunableFloat( "/Config/ClimberPositions/Reset", -5000.0, persistent=True )

    def __init__(self, climber:ClimberIO):
        self.climber = climber
        self.climberInputs = climber.ClimberIOInputs()
        self.climberLogger = NetworkTableInstance.getDefault().getStructTopic( "/Climber", ClimberIO.ClimberIOInputs ).publish()
        self.climberMeasuredLogger = NetworkTableInstance.getDefault().getTable( "/Logging/Climber" )

        self.offline = NTTunableBoolean( "/DisableSubsystem/Climber", False, persistent=True )

    def periodic(self):
        # Logging
        self.climber.updateInputs( self.climberInputs )
        self.climberLogger.set( self.climberInputs )
        #NewLogger# Logger.getInstance().processInputs( "Climber", self.climberInputs )
        
        # Run Subsystem
        if DriverStation.isDisabled() or self.offline.get():
            self.stop()

        if False: #self.isCharacterizing.get():
            self.climber.runCharacterization( self.charSettingsVolts.get(), self.charSettingsRotation.get() )
        else:
             self.climber.run()

        # Post Run Logging
        self.climberMeasuredLogger.putNumberArray( "Measured", self.climber.getPosition() )
        self.climberMeasuredLogger.putNumberArray( "Setpoint", self.climber.getSetpoint() )

    def set(self, leftPosition:float, rightPosition:float, override:bool = False):
        if not override:
            leftPosition = min( max( leftPosition, Climber.ClimberPositions.Bottom.get() ), Climber.ClimberPositions.Top.get() )
            rightPosition = min( max( leftPosition, Climber.ClimberPositions.Bottom.get() ), Climber.ClimberPositions.Top.get() )
        self.climber.setPosition( leftPosition, rightPosition )

    def move(self, leftRate:float, rightRate:float):
        self.climber.movePosition( leftRate, rightRate )

    def stop(self):
        currentPos = self.climber.getPosition()
        self.set( currentPos[0], currentPos[1] )

    def setBrake(self, brake:bool) -> None:
        self.climber.setBrake(brake)
    
    def getPosition(self) -> [float, float]:
        return self.climber.getPosition()

    def atSetpoint(self, errorRange:float = 100.0) -> bool:
        status = self.climber.atSetpoint(errorRange)
        return ( status[0] and status[1] )

    def reset(self) -> None:
        self.climber.resetPosition( Climber.ClimberPositions.Bottom.get() )