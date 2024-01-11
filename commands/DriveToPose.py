# Import Python
import math

# Import FRC
from commands2 import Command
from wpilib import Timer
from wpimath.kinematics import SwerveDrive4Kinematics, SwerveModuleState
from wpimath.controller import PIDController, ProfiledPIDControllerRadians, HolonomicDriveController
from wpimath.geometry import Translation2d
from wpimath.trajectory import Trajectory, TrajectoryConfig, TrajectoryGenerator, TrapezoidProfileRadians
#from pathplannerlib import PathConstraints, PathPlanner, PathPlannerTrajectory, PathPoint

# Import Subsystems and Commands
from subsystems import *

class DriveToPose(Command):
    _m_controller: HolonomicDriveController = None
    swerveDrive: SwerveDrive = None
    
    def __init__(self, swerveDrive:SwerveDrive, getTargetPose:typing.Callable[[], Pose2d]):
        super().__init__()
        self.swerveDrive = swerveDrive
        self.getTargetPose = getTargetPose
        self.addRequirements( swerveDrive )
        self.setName( "DriveToPose" )

    def initialize(self):
        ### PID Controllers
        self._m_controller = HolonomicDriveController(
            PIDController( 200, 0, 0 ),
            PIDController( 200, 0, 0 ),
            ProfiledPIDControllerRadians(
                1, 0, 0,
                TrapezoidProfileRadians.Constraints(
                    self.swerveDrive.maxVelocity.get(),
                    self.swerveDrive.maxAngularVelocity.get()
                )
            )
        )
        self._m_controller.setTolerance( Pose2d( Translation2d( 0.1, 0.1 ), Rotation2d(0.01) ) )
        self._m_controller.getXController().reset()
        self._m_controller.getYController().reset()
        self._m_controller.getThetaController().reset( self.swerveDrive.getRobotAngle().radians() )

        #self._m_controller = self.swerveDrive.getHolonomicPIDController()
        #self._m_xPid = self._m_controller.getXController()
        #self._m_yPid = self._m_controller.getYController()
        #self._m_tPid = self._m_controller.getThetaController()
        
        # Pid Controller Resets
        #self._m_xPid.reset()
        #self._m_yPid.reset()
        #self._m_tPid.reset( self.swerveDrive.getRobotAngle().radians() )

    def execute(self):
        startPose = self.swerveDrive.getPose()
        targetPose = self.getTargetPose()

        #x = self._m_xPid.calculate( startPose.X(), targetPose.X() )
        #y = self._m_yPid.calculate( startPose.Y(), targetPose.Y() )
        #r = self._m_tPid.calculate( startPose.rotation().radians(), targetPose.rotation().radians() )

        #x = min( max( x, -1.0 ), 1.0 )
        #y = min( max( y, -1.0 ), 1.0 )
        #r = min( max( r, -1.0 ), 1.0 )

        # Percentage Run
        #self.swerveDrive.runPercentageInputs( x, y, r )
        
        # Chassis Speed Run
        #speeds = ChassisSpeeds.fromFieldRelativeSpeeds( x, y, r, self.swerveDrive.getRobotAngle() )

        heading = targetPose.relativeTo( startPose ).rotation()
        cSpeeds = self._m_controller.calculate( startPose, targetPose, self.swerveDrive.maxVelocity.get(), Rotation2d(0) ) #heading )
        self.swerveDrive.runChassisSpeeds( cSpeeds )

    def end(self, interrupted:bool) -> None:
        #self.swerveDrive.stop()
        pass

    def isFinished(self) -> bool:
        #xDone = self._m_xPid.atSetpoint()
        #yDone = self._m_yPid.atSetpoint()
        #tDone = self._m_tPid.atSetpoint()
        #return xDone and yDone and tDone

        return self._m_controller.atReference()