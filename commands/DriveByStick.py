### Imports
# Python Imports
import typing
import math

# FRC Component Imports
from commands2 import CommandBase
from wpimath import applyDeadband
from wpimath.controller import ProfiledPIDControllerRadians
from wpimath.geometry import Rotation2d
from wpimath.filter import SlewRateLimiter
from wpimath.kinematics import ChassisSpeeds
from wpimath.trajectory import TrapezoidProfileRadians

# Our Imports
from subsystems.SwerveDrive import SwerveDrive
from util import *

# Default Drive Command Class
class DriveByStick(CommandBase):
    def __init__( self,
                  swerveDrive:SwerveDrive,
                  velocityX:typing.Callable[[], float],
                  velocityY:typing.Callable[[], float],
                  holonomicX:typing.Callable[[], float] = ( lambda: 0.0 ),
                  holonomicY:typing.Callable[[], float] = ( lambda: 0.0 ), 
                  rotate:typing.Callable[[], float] = ( lambda: 0.0 )
                ):
        # CommandBase Initiation Configurations
        super().__init__()
        self.setName( "DriveByStick" )
        self.addRequirements( swerveDrive )

        # Tunables
        self.deadband = NTTunableFloat( "DriveByStick/Deadband", 0.04 )

        self.finetuneEnabled = NTTunableBoolean( "DriveByStick/Control/FineEnabled", False )
        self.ctlFineVelocity = NTTunableFloat( "DriveByStick/Control/Fine/Velocity", 0.4 )
        self.ctlFineHolonomic = NTTunableFloat( "DriveByStick/Control/Fine/Holonomic", 0.4 )
        self.ctlFineRotation = NTTunableFloat( "DriveByStick/Control/Fine/Rotation", 0.4 )

        self.ctlFullVelocity = NTTunableFloat( "DriveByStick/Control/Full/Velocity", 0.8 )
        self.ctlFullHolonomic = NTTunableFloat( "DriveByStick/Control/Full/Holonomic", 0.8 )
        self.ctlFullRotation = NTTunableFloat( "DriveByStick/Control/Full/Rotation", 0.8 )

        self.theta_kP = NTTunableFloat( "DriveByStick/Theta/kP", 0.0, self.updateThetaPIDController )
        self.theta_kI = NTTunableFloat( "DriveByStick/Theta/kI", 0.0, self.updateThetaPIDController )
        self.theta_kD = NTTunableFloat( "DriveByStick/Theta/kD", 0.0, self.updateThetaPIDController )
        self.theta_kV = NTTunableFloat( "DriveByStick/Theta/kV", 0.0, self.updateThetaPIDController )
        self.theta_kA = NTTunableFloat( "DriveByStick/Theta/kA", 0.0, self.updateThetaPIDController )

        self.srlV = NTTunableFloat( "DriveByStick/SlewRateLimiter/Velocity", 3.0, self.updateSlewRateLimiterVelocity )
        self.srlH = NTTunableFloat( "DriveByStick/SlewRateLimiter/Holonomic", 3.0, self.updateSlewRateLimiterHolonomic )
        self.srlR = NTTunableFloat( "DriveByStick/SlewRateLimiter/Rotation", 3.0, self.updateSlewRateLimiterRotation )

        # This Command Global Properties
        self.drive = swerveDrive
        self.vX = velocityX
        self.vY = velocityY
        self.hX = holonomicX
        self.hY = holonomicY
        self.rO = rotate

        # Slew Rate Limiters
        self.updateSlewRateLimiterVelocity()
        self.updateSlewRateLimiterHolonomic()
        self.updateSlewRateLimiterRotation()

        # Theta PID Controller
        self.tPid = ProfiledPIDControllerRadians(
            self.theta_kP.get(),
            self.theta_kI.get(),
            self.theta_kD.get(),
            TrapezoidProfileRadians.Constraints(
                self.theta_kV.get(),
                self.theta_kA.get()
            )
        )
        self.updateThetaPIDController()

    def updateSlewRateLimiterVelocity(self):
        self.srl_vX = SlewRateLimiter( self.srlV.get() )
        self.srl_vY = SlewRateLimiter( self.srlV.get() )

    def updateSlewRateLimiterHolonomic(self):
        self.srl_hX = SlewRateLimiter( self.srlH.get() )
        self.srl_hY = SlewRateLimiter( self.srlH.get() )

    def updateSlewRateLimiterRotation(self):
        self.srl_rO = SlewRateLimiter( self.srlR.get() )

    def updateThetaPIDController(self):
        self.tPid.setPID( self.theta_kP.get(), self.theta_kI.get(), self.theta_kD.get() )
        self.tPid.setConstraints(
            TrapezoidProfileRadians.Constraints(
                self.theta_kV.get(),
                self.theta_kA.get()
            )
        )
        self.resetThetaPIDController()

    def resetThetaPIDController(self) -> None:
        self.tPid.reset(
            self.drive.getRobotAngle().radians(),
            self.drive.getRotationVelocity()
        )

    def initialize(self) -> None:
        self.resetThetaPIDController()

    def execute(self) -> None:
        # Get Input Values
        x = -self.vX()
        y = -self.vY()
        hX = -self.hX()
        hY = -self.hY()
        r = self.rO()

        # Calculate Deadband
        x = applyDeadband( x, self.deadband.get() ) 
        y = applyDeadband( y, self.deadband.get() )
        hX = applyDeadband( hX, self.deadband.get() )
        hY = applyDeadband( hY, self.deadband.get() )
        r = applyDeadband( r, self.deadband.get() )

        # Square the Inputs
        x *= abs( x )
        y *= abs( y )
        hX *= abs( hX )
        hY *= abs( hY )
        r *= abs( r )

        # Slew Rate Limiter
        x = self.srl_vX.calculate( x )
        y = self.srl_vY.calculate( y )
        hX = self.srl_hX.calculate( hX )
        hY = self.srl_hY.calculate( hY )
        r = self.srl_rO.calculate( r )

        # Calculate Fine Tuned Controls
        magV = self.ctlFullVelocity.get() if not self.finetuneEnabled.get() else self.ctlFineVelocity.get()
        magH = self.ctlFullHolonomic.get() if not self.finetuneEnabled.get() else self.ctlFineHolonomic.get()
        magR = self.ctlFullRotation.get() if not self.finetuneEnabled.get() else self.ctlFineRotation.get()           
        x *= magV
        y *= magV
        r *= magR

        # Calculate Rotation via Holonomic or Buttons
        if abs(hX) > 0.1 or abs(hY) > 0.1:
            #pid = self.tPid
            mag = math.sqrt( hX*hX + hY*hY ) * magH
            robotAngle:float = self.drive.getRobotAngle().radians()
            goalAngle:float = Rotation2d( x=hX, y=hY ).radians()
            target = self.tPid.calculate(robotAngle, goalAngle)
            r = target * mag
            r = min( max( r, -1.0 ), 1.0 )
        elif abs(r) > 0.1:
            self.resetThetaPIDController()

        # Send ChassisSpeeds
        self.drive.runPercentageInputs(x, y, r)

    def end(self, interrupted:bool) -> None: pass
    def isFinished(self) -> bool: return False
    def runsWhenDisabled(self) -> bool: return False