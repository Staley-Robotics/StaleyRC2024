### Imports
# Python Imports
import typing
import math

# FRC Component Imports
from commands2 import Command
from wpilib import DriverStation
from wpimath import applyDeadband
from wpimath.controller import ProfiledPIDControllerRadians
from wpimath.geometry import Rotation2d
from wpimath.filter import SlewRateLimiter
from wpimath.kinematics import ChassisSpeeds
from wpimath.trajectory import TrapezoidProfileRadians

# Our Imports
from subsystems import SwerveDrive
from util import *

# Default Drive Command Class
class DriveAndAim(Command):
    def __init__( self,
                  swerveDrive:SwerveDrive,
                  velocityX:typing.Callable[[], float],
                  velocityY:typing.Callable[[], float]
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.setName( "DriveAndAim" )
        self.addRequirements( swerveDrive )

        # Tunables
        self.deadband = NTTunableFloat( "/CmdConfig/DriveByStick/Deadband", 0.04 )

        self.finetuneEnabled = NTTunableBoolean( "/CmdConfig/DriveByStick/Control/FineEnabled", False )
        self.ctlFineVelocity = NTTunableFloat( "/CmdConfig/DriveByStick/Control/Fine/Velocity", 0.4 )
        self.ctlFineHolonomic = NTTunableFloat( "/CmdConfig/DriveByStick/Control/Fine/Holonomic", 0.4 )
        self.ctlFineRotation = NTTunableFloat( "/CmdConfig/DriveByStick/Control/Fine/Rotation", 0.4 )

        self.ctlFullVelocity = NTTunableFloat( "/CmdConfig/DriveByStick/Control/Full/Velocity", 0.8 )
        self.ctlFullHolonomic = NTTunableFloat( "/CmdConfig/DriveByStick/Control/Full/Holonomic", 0.8 )
        self.ctlFullRotation = NTTunableFloat( "/CmdConfig/DriveByStick/Control/Full/Rotation", 0.8 )

        # self.srlV = NTTunableFloat( "/CmdConfig/DriveByStick/SlewRateLimiter/Velocity", 3.0, self.updateSlewRateLimiterVelocity )
        # self.srlH = NTTunableFloat( "/CmdConfig/DriveByStick/SlewRateLimiter/Holonomic", 3.0, self.updateSlewRateLimiterHolonomic )
        # self.srlR = NTTunableFloat( "/CmdConfig/DriveByStick/SlewRateLimiter/Rotation", 3.0, self.updateSlewRateLimiterRotation )

        # This Command Global Properties
        self.drive = swerveDrive
        self.vX = velocityX
        self.vY = velocityY

        # # Slew Rate Limiters
        # self.updateSlewRateLimiterVelocity()
        # self.updateSlewRateLimiterHolonomic()
        # self.updateSlewRateLimiterRotation()

        # Target
        self.targetBlue = Translation2d( 0.25, 5.50 )
        self.targetRed = CrescendoUtil.convertTranslationToRedAlliance( self.targetBlue )
        self.target = self.targetBlue

    # def updateSlewRateLimiterVelocity(self):
    #     self.srl_vX = SlewRateLimiter( self.srlV.get() )
    #     self.srl_vY = SlewRateLimiter( self.srlV.get() )

    # def updateSlewRateLimiterHolonomic(self):
    #     self.srl_hX = SlewRateLimiter( self.srlH.get() )
    #     self.srl_hY = SlewRateLimiter( self.srlH.get() )

    # def updateSlewRateLimiterRotation(self):
    #     self.srl_rO = SlewRateLimiter( self.srlR.get() )

    def initialize(self) -> None:
        # Get Holonomic PID
        self.tPid = self.drive.getHolonomicDriveController().getThetaController()
        self.tPid.reset( self.drive.getRobotAngle().radians(), self.drive.getRotationVelocity() )
        
        # Update Target to Red Alliance, if necessary
        if DriverStation.getAlliance() == DriverStation.Alliance.kRed:
            self.target = self.targetRed
        elif DriverStation.getAlliance() == DriverStation.Alliance.kBlue:
            self.target = self.targetBlue

    def execute(self) -> None:
        # Get Input Values
        x = -self.vX()
        y = -self.vY()

        # Calculate Deadband
        x = applyDeadband( x, self.deadband.get() ) 
        y = applyDeadband( y, self.deadband.get() )

        # Square the Inputs
        x *= abs( x )
        y *= abs( y )

        # Slew Rate Limiter
        #x = self.srl_vX.calculate( x )
        #y = self.srl_vY.calculate( y )

        # Calculate Fine Tuned Controls
        magV = self.ctlFullVelocity.get() if not self.finetuneEnabled.get() else self.ctlFineVelocity.get()
        magH = self.ctlFullHolonomic.get() if not self.finetuneEnabled.get() else self.ctlFineHolonomic.get()
        #magR = self.ctlFullRotation.get() if not self.finetuneEnabled.get() else self.ctlFineRotation.get()           
        x *= magV
        y *= magV
        #r *= magR

        # Calculate Rotation To Target
        robotAngle:float = self.drive.getRobotAngle().radians()
        robotPose = self.drive.getPose()
        hX = self.target.X() - robotPose.X()
        hY = self.target.Y() - robotPose.Y()
        goalAngle:float = Rotation2d( x=hX, y=hY ).radians()
        r = self.tPid.calculate(robotAngle, goalAngle)
        r = min( max( r, -1.0 ), 1.0 )

        # Send ChassisSpeeds
        self.drive.runPercentageInputs(x, y, r)

    def end(self, interrupted:bool) -> None: pass
    def isFinished(self) -> bool: return False
    def runsWhenDisabled(self) -> bool: return False