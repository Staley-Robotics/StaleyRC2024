from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import DriverStation

from util import *
from .ClimberIO import ClimberIO

class Climber(Subsystem):
    class ClimberPositions:
        Bottom = NTTunableFloat( "/Config/ClimberPositions/Bottom", 0.0, persistent=True )
        Top = NTTunableFloat( "/Config/ClimberPositions/Top", 7000.0, persistent=True )
        Reset = NTTunableFloat( "/Config/ClimberPositions/Reset", -5000.0, persistent=True )

    def __init__(self, lClimber:ClimberIO, rClimber:ClimberIO):
        self.lClimber = lClimber
        self.lClimberInputs = lClimber.ClimberIOInputs()
        self.lClimberLogger = NetworkTableInstance.getDefault().getStructTopic( "/Climber/Left", ClimberIO.ClimberIOInputs ).publish()
        self.lClimberMeasuredLogger = NetworkTableInstance.getDefault().getTable( "/Logging/Climber/Left" )

        self.rClimber = rClimber
        self.rClimberInputs = rClimber.ClimberIOInputs()
        self.rClimberLogger = NetworkTableInstance.getDefault().getStructTopic( "/Climber/Right", ClimberIO.ClimberIOInputs ).publish()
        self.rClimberMeasuredLogger = NetworkTableInstance.getDefault().getTable( "/Logging/Climber/Right" )

        self.offline = NTTunableBoolean( "/DisableSubsystem/Climber", False, persistent=True )

    def periodic(self):
        # Logging
        self.lClimber.updateInputs( self.lClimberInputs )
        self.lClimberLogger.set( self.lClimberInputs )

        self.rClimber.updateInputs( self.rClimberInputs )
        self.rClimberLogger.set( self.rClimberInputs )
        
        # Run Subsystem
        if DriverStation.isDisabled() or self.offline.get():
            self.stop()

        if False: #self.isCharacterizing.get():
            self.climber.runCharacterization( self.charSettingsVolts.get(), self.charSettingsRotation.get() )
        else:
             self.lClimber.run()
             self.rClimber.run()

        # Post Run Logging
        self.lClimberMeasuredLogger.putNumber( "Measured", self.lClimber.getPosition() )
        self.lClimberMeasuredLogger.putNumber( "Setpoint", self.lClimber.getSetpoint() )

        self.rClimberMeasuredLogger.putNumber( "Measured", self.lClimber.getPosition() )
        self.rClimberMeasuredLogger.putNumber( "Setpoint", self.rClimber.getSetpoint() )

    def set(self, leftPosition:float, rightPosition:float, override:bool = False):
        if not override:
            leftPosition = min( max( leftPosition, Climber.ClimberPositions.Bottom.get() ), Climber.ClimberPositions.Top.get() )
            rightPosition = min( max( rightPosition, Climber.ClimberPositions.Bottom.get() ), Climber.ClimberPositions.Top.get() )
        
        self.lClimber.setPosition( leftPosition )
        self.rClimber.setPosition( rightPosition )

    def move(self, leftRate:float, rightRate:float):
        self.lClimber.movePosition( leftRate )
        self.rClimber.movePosition( rightRate )

    def stop(self):
        lCurrentPos = self.lClimber.getPosition()
        rCurrentPos = self.rClimber.getPosition()
        self.set( lCurrentPos, rCurrentPos )

    def setBrake(self, brake:bool) -> None:
        self.lClimber.setBrake(brake)
        self.rClimber.setBrake(brake)
    
    def getPosition(self) -> [float, float]:
        return [ self.lClimber.getPosition(), self.rClimber.getPosition() ]

    def atSetpoint(self, errorRange:float = 25.0) -> bool:
        lStatus = self.lClimber.atSetpoint(errorRange)
        rStatus = self.rClimber.atSetpoint(errorRange)
        return ( lStatus and rStatus )

    def reset(self) -> None:
        self.lClimber.resetPosition( Climber.ClimberPositions.Bottom.get() )
        self.rClimber.resetPosition( Climber.ClimberPositions.Bottom.get() )

    def atBottom(self) -> bool:
        lBottom = self.lClimber.atSetpoint()
        rBottom = self.rClimber.atSetpoint()
        return lBottom and rBottom