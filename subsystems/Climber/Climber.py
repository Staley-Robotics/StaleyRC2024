from commands2 import Subsystem
from ntcore import NetworkTableInstance
from wpilib import DriverStation

from util import *
from .ClimberIO import ClimberIO

class Climber(Subsystem):
    class ClimberPositions:
        Timer = NTTunableFloat( "/Config/ClimberPositions/Timer", 0.25, persistent=True )
        Bottom = NTTunableFloat( "/Config/ClimberPositions/Bottom", 0.0, persistent=True )
        Top = NTTunableFloat( "/Config/ClimberPositions/Top", 7000.0, persistent=True )
        Reset = NTTunableFloat( "/Config/ClimberPositions/Reset", -5000.0, persistent=True )

    def __init__(self, lClimber:ClimberIO, rClimber:ClimberIO):
        self.lClimber = lClimber
        self.lClimberInputs = lClimber.ClimberIOInputs()
        #self.lClimberLogger = NetworkTableInstance.getDefault().getStructTopic( "/Climber/Left", ClimberIO.ClimberIOInputs ).publish()

        self.rClimber = rClimber
        self.rClimberInputs = rClimber.ClimberIOInputs()
        #self.rClimberLogger = NetworkTableInstance.getDefault().getStructTopic( "/Climber/Right", ClimberIO.ClimberIOInputs ).publish()

        self.climberLogger = NetworkTableInstance.getDefault().getStructArrayTopic( "/Climber", ClimberIO.ClimberIOInputs ).publish()
        self.lClimberMeasuredLogger = NetworkTableInstance.getDefault().getTable( "/Logging/Climber/Left" )
        self.rClimberMeasuredLogger = NetworkTableInstance.getDefault().getTable( "/Logging/Climber/Right" )

        self.offline = NTTunableBoolean( "/DisableSubsystem/Climber", False, persistent=True )

    def periodic(self):
        # Logging
        self.lClimber.updateInputs( self.lClimberInputs )
        self.rClimber.updateInputs( self.rClimberInputs )
        self.climberLogger.set( [self.lClimberInputs, self.rClimberInputs] )
        # self.lClimberLogger.set( self.lClimberInputs )
        # self.rClimberLogger.set( self.rClimberInputs )
        
        # Run Subsystem
        if DriverStation.isDisabled() or self.offline.get():
            self.stop()

        if False: #self.isCharacterizing.get():
            self.climber.runCharacterization( self.charSettingsVolts.get(), self.charSettingsRotation.get() )
        else:
             self.lClimber.run()
             self.rClimber.run()

        # Post Run Logging
        self.lClimberMeasuredLogger.putNumber( "Measured", self.lClimber.getRate() )
        self.lClimberMeasuredLogger.putNumber( "Setpoint", self.lClimber.getSetpoint() )

        self.rClimberMeasuredLogger.putNumber( "Measured", self.rClimber.getRate() )
        self.rClimberMeasuredLogger.putNumber( "Setpoint", self.rClimber.getSetpoint() )

    def set(self, leftRate:float, rightRate:float):        
        self.lClimber.setRate( leftRate )
        self.rClimber.setRate( rightRate )

    def stop(self):
        self.set( 0.0, 0.0 )

    def setBrake(self, brake:bool) -> None:
        self.lClimber.setBrake(brake)
        self.rClimber.setBrake(brake)
    
    def getRate(self) -> [float, float]:
        return [ self.lClimber.getRate(), self.rClimber.getRate() ]
    
    def atTop(self) -> bool:
        return self.lClimber.atTop() and self.rClimber.atTop()
    
    def atBottom(self) -> bool:
        return self.lClimber.atBottom() and self.rClimber.atBottom()
