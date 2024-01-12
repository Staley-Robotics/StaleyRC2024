"""
Description: 4 Wheel Swerve Drive Chassis
Version:  1
Date:  2024-01-09

Dependencies:
- SwerveModule:  SwerveModule
- Gyro:          Gyro
"""

### Imports
# Python Imports
import typing
import math

# FRC Component Imports
from commands2 import Subsystem
from wpilib import SmartDashboard, Timer, DriverStation, RobotBase, Field2d
from wpimath.controller import PIDController, ProfiledPIDControllerRadians, HolonomicDriveController
from wpimath.estimator import SwerveDrive4PoseEstimator
from wpimath.geometry import Translation2d, Rotation2d, Pose2d
from wpimath.kinematics import SwerveDrive4Kinematics, ChassisSpeeds, SwerveModulePosition, SwerveModuleState
from wpimath.trajectory import TrapezoidProfileRadians
from ntcore import *

# Our Imports
from util import *
from .SwerveModule import SwerveModule
from .Gyro import Gyro

class SwerveDrive(Subsystem):
    """
    SwerveDrive Subsystem Class used to operate a 4 Wheel SwerveDrive Chassis
    """
    
    def __init__( self,
                  modules:typing.Tuple[ SwerveModule,
                                        SwerveModule,
                                        SwerveModule,
                                        SwerveModule ],
                  gyro:Gyro=Gyro() ):
        """
        Initialization of a SwerveDrive
        """
        # Subsystem Setup
        self.setName( "SwerveDrive" )

        # Robot Name
        self.robotName = "Robot"
        if not RobotBase.isReal(): self.robotName = "SimRobot"

        # Get Tunable Properties
        self.isCharacterizing = NTTunableBoolean( "/Characterizing/Enabled", False, persistent = True )
        self.charMaxVelocity = NTTunableFloat( "/Characterizing/SwerveDrive/maxVelocity", 3.70, persistent = True )
        self.charMaxAngularVelocity = NTTunableFloat( "/Characterizing/SwerveDrive/maxAngularVelocity", 2 * math.pi, persistent = True )
        self.charMOI = NTTunableFloat( "/Characterizing/SwerveDrive/moi", 0.250, persistent = True )
        
        self.maxVelocity = NTTunableFloat( "SwerveDrive/maxVelocity", 3.70 )
        self.maxAngularVelocity = NTTunableFloat( "SwerveDrive/maxAngularVelocity", 2 * math.pi )
        self.fieldRelative = NTTunableBoolean( "SwerveDrive/fieldRelative", True )

        self.pidX_kP = NTTunableFloat( "SwerveDrive/holonomicDriveController/x/kP", 1, self.updateHolonomicDriveController )
        self.pidX_kI = NTTunableFloat( "SwerveDrive/holonomicDriveController/x/kI", 0, self.updateHolonomicDriveController )
        self.pidX_kD = NTTunableFloat( "SwerveDrive/holonomicDriveController/x/kD", 0, self.updateHolonomicDriveController )
        self.pidY_kP = NTTunableFloat( "SwerveDrive/holonomicDriveController/y/kP", 1, self.updateHolonomicDriveController )
        self.pidY_kI = NTTunableFloat( "SwerveDrive/holonomicDriveController/y/kI", 0, self.updateHolonomicDriveController )
        self.pidY_kD = NTTunableFloat( "SwerveDrive/holonomicDriveController/y/kD", 0, self.updateHolonomicDriveController )
        self.pidT_kP = NTTunableFloat( "SwerveDrive/holonomicDriveController/theta/kP", 1, self.updateHolonomicDriveController )
        self.pidT_kI = NTTunableFloat( "SwerveDrive/holonomicDriveController/theta/kI", 0, self.updateHolonomicDriveController )
        self.pidT_kD = NTTunableFloat( "SwerveDrive/holonomicDriveController/theta/kD", 0, self.updateHolonomicDriveController )
        self.pidH_tDistance = NTTunableFloat( "SwerveDrive/holonomicDriveController/tolerance/distance", 0.0254, self.updateHolonomicDriveController )
        self.pidH_tRotation = NTTunableFloat( "SwerveDrive/holonomicDriveController/tolerance/rotation", 0.008, self.updateHolonomicDriveController )

        # Gyro and Modules
        self.gyro = gyro
        self.modules = modules

        self.gyroInputs = self.gyro.GyroInputs()
        self.moduleInputs = []
        for mod in self.modules:
            self.moduleInputs.append( mod.SwerveModuleInputs() )

        # Kinematics
        self.kinematics = SwerveDrive4Kinematics(
            self.modules[0].getReferencePosition(),
            self.modules[1].getReferencePosition(),
            self.modules[2].getReferencePosition(),
            self.modules[3].getReferencePosition()
        )

        # Odometry
        self.odometry = SwerveDrive4PoseEstimator(
            self.getKinematics(),
            self.gyro.getRotation2d(),
            self.getModulePositions(),
            Pose2d(Translation2d(0,0), Rotation2d())
        )

        # PID Controllers for Drive Motion
        self.hPid:HolonomicDriveController = None
        self.updateHolonomicDriveController()

        # NT Publishing
        if not NetworkTableInstance.getDefault().hasSchema( "SwerveModuleState" ):        
            self.ntSwerveModuleStatesCurrent = NetworkTableInstance.getDefault().getStructTopic( "/StartSchema/SwerveModuleState", SwerveModuleState ).publish( PubSubOptions() )
            self.ntSwerveModuleStatesCurrent.set( SwerveModuleState() ) 
            self.ntSwerveModuleStatesCurrent.close()
        if not NetworkTableInstance.getDefault().hasSchema( "SwerveModuleInputs" ):        
            self.ntSwerveModuleStatesCurrent = NetworkTableInstance.getDefault().getStructTopic( "/StartSchema/SwerveModuleInputs", SwerveModule.SwerveModuleInputs ).publish( PubSubOptions() )
            self.ntSwerveModuleStatesCurrent.set( SwerveModule.SwerveModuleInputs() ) 
            self.ntSwerveModuleStatesCurrent.close()

        self.ntGyroInputs = NetworkTableInstance.getDefault().getStructTopic( "/SwerveDrive/Gyro", Gyro.GyroInputs ).publish()
        self.ntModuleInputs = NetworkTableInstance.getDefault().getStructArrayTopic( "/SwerveDrive/Modules", SwerveModule.SwerveModuleInputs ).publish()

        self.ntRobotPose2d = NetworkTableInstance.getDefault().getStructTopic( "/Logging/Odometry/Robot", Pose2d ).publish()
        self.ntChassisSpeedsCurrent = NetworkTableInstance.getDefault().getStructTopic( "/Logging/ChassisSpeeds/Current", ChassisSpeeds ).publish()
        self.ntChassisSpeedsNext = NetworkTableInstance.getDefault().getStructTopic( "/Logging/ChassisSpeeds/Next", ChassisSpeeds ).publish()
        self.ntSwerveModuleStatesCurrent = NetworkTableInstance.getDefault().getStructArrayTopic( "/Logging/SwerveModuleStates/Current", SwerveModuleState ).publish( PubSubOptions() )
        self.ntSwerveModuleStatesNext = NetworkTableInstance.getDefault().getStructArrayTopic( "/Logging/SwerveModuleStates/Next", SwerveModuleState ).publish()

    def periodic(self):
        """
        SwerveDrive Periodic Loop
        """
        # Logging
        self.gyro.updateInputs( self.gyroInputs )
        for x in range(len(self.modules)):
            self.modules[x].updateInputs( self.moduleInputs[x] )
        
        self.ntGyroInputs.set( self.gyroInputs )
        self.ntModuleInputs.set( self.moduleInputs )

        # Run Modules
        if DriverStation.isDisabled():
            self.stop()
        elif self.isCharacterizing.get():
            #for module in self.modules:
            #    module.driveMotor.set( self.characterizationVolts.get() )
            pass
        else:
            for module in self.modules:
                module.run()

        # Odometry from Module Position Data
        pose = self.getOdometry().updateWithTime(
            Timer.getFPGATimestamp(),
            self.gyro.getRotation2d(),
            self.getModulePositions()
        )

        # Logging: RobotPose, ChassisSpeeds, SwerveModuleStates Speeds
        self.ntRobotPose2d.set( pose )
        self.ntChassisSpeedsCurrent.set( self.getChassisSpeeds() )
        self.ntChassisSpeedsNext.set( self.getChassisSpeedsSetpoint() )
        self.ntSwerveModuleStatesCurrent.set( self.getModuleStates() )
        self.ntSwerveModuleStatesNext.set( self.getModuleSetpoints() )
           
    def simulationPeriodic(self) -> None:
        """
        SwerveDrive Simulation Periodic Loop
        """
        pass

    def isFieldRelative(self) -> bool:
        """
        Get the Field Relative Drive State of this SwerveDrive

        :returns: boolean
        """
        return self.fieldRelative.get()

    def getKinematics(self) -> SwerveDrive4Kinematics:
        """
        Get the Kinematics configuration of this SwerveDrive

        :returns: SwerveDrive4Kinematics
        """
        return self.kinematics
       
    def getOdometry(self) -> SwerveDrive4PoseEstimator:
        """
        Get The Current Odometry (fused with Vision Data) of this SwerveDrive

        :returns: SwerveDrive4PoseEstimator
        """
        return self.odometry

    def updateHolonomicDriveController(self) -> None:
        """
        Update the HolonomicDriveController configuration for this SwerveDrive

        :returns: HolonomicDriveController
        """
        x = PIDController(
            self.pidX_kP.get(),
            self.pidX_kI.get(),
            self.pidX_kD.get()
        )
        y = PIDController(
            self.pidY_kP.get(),
            self.pidY_kI.get(),
            self.pidY_kD.get()
        )
        theta = ProfiledPIDControllerRadians(
            self.pidT_kP.get(),
            self.pidT_kI.get(),
            self.pidT_kD.get(),
            TrapezoidProfileRadians.Constraints(
                self.maxAngularVelocity.get(),
                self.maxAngularVelocity.get() * 2
            )
        )
        theta.enableContinuousInput( -math.pi, math.pi )
        theta.reset( self.getRobotAngle().radians(), self.getRotationVelocity() )

        self.hPid = HolonomicDriveController( x, y, theta )
        self.hPid.setTolerance(
            Pose2d(
                Translation2d( 
                    self.pidH_tDistance.get(),
                    self.pidH_tDistance.get()
                ),
                Rotation2d( self.pidH_tRotation.get() )
            )
        )

        self.resetHolonomicDriveController()

    def resetHolonomicDriveController(self) -> None:
        """
        Reset the HolonomicDriveController for this SwerveDrive
        """
        self.hPid.getXController().reset()
        self.hPid.getYController().reset()
        self.hPid.getThetaController().reset(
            self.getRobotAngle().radians(),
            self.getRotationVelocity()
        )

    def getHolonomicDriveController(self) -> HolonomicDriveController:
        """
        Get the HolonomicDriveController for this SwerveDrive

        :returns: HolonomicDriveController
        """
        #self.resetHolonomicDriveController()
        return self.hPid

    def getPose(self) -> Pose2d:
        """
        Get the Current Pose from the Odometry data of this SwerveDrive
        
        :returns: Pose2d
        """
        return self.getOdometry().getEstimatedPosition()
    
    def getRobotAngle(self) -> Rotation2d:
        """
        Get the Current Rotation based on the gyroscope of this SwerveDrive 

        :returns: Rotation2d
        """
        return self.gyro.getRotation2d()

    def getRotationVelocity(self) -> float:
        """
        Get the Angular Velocity of this SwerveDrive
        
        :returns: float in radians per second
        """
        return self.getChassisSpeeds().omega
    
    def getChassisSpeeds(self) -> ChassisSpeeds:
        """
        Get the Current Chassis Speeds based on the Wheel Measurements
        
        :returns: ChassisSpeeds in meters per second velocity in x and y direction and rotations per
        """
        return self.getKinematics().toChassisSpeeds( self.getModuleStates() )
    
    def getChassisSpeedsSetpoint(self) -> ChassisSpeeds:
        """
        Get the Chassis Speeds based on the Wheel Measurements
        
        :returns: ChassisSpeeds in meters per second velocity in x and y direction and rotations per
        """
        return self.getKinematics().toChassisSpeeds( self.getModuleSetpoints() )

    def getModuleSetpoints(self) -> typing.Tuple[ SwerveModuleState,
                                               SwerveModuleState,
                                               SwerveModuleState,
                                               SwerveModuleState ]:
        """
        Returns all of the SwerveModuleStates of the SwerveModules on this SwerveDrive

        :returns: Tuple of SwerveModuleStates (velocity, rotation)
        """
        return tuple( modules.getModuleSetpoint() for modules in self.modules )

    def getModuleStates(self) -> typing.Tuple[ SwerveModuleState,
                                               SwerveModuleState,
                                               SwerveModuleState,
                                               SwerveModuleState ]:
        """
        Returns all of the SwerveModuleStates of the SwerveModules on this SwerveDrive

        :returns: Tuple of SwerveModuleStates (velocity, rotation)
        """
        return tuple( modules.getModuleState() for modules in self.modules )

    def getModulePositions(self) -> typing.Tuple[ SwerveModulePosition,
                                                  SwerveModulePosition,
                                                  SwerveModulePosition,
                                                  SwerveModulePosition ]:
        """
        Returns all of the SwerveModulePositions of the SwerveModules on this SwerveDrive

        :returns: Tuple of SwerveModulePosition (distance, rotation)
        """
        return tuple( modules.getModulePosition() for modules in self.modules )
    
    def stop(self): # -> CommandBase:
        """
        Stops this SwerveDrive
        """
        self.runChassisSpeeds( ChassisSpeeds(0,0,0) )
        
    def runPercentageInputs(self, x:float = 0.0, y:float = 0.0, r:float = 0.0) -> None:
        """
        Runs this SwerveDrive in x,y velocities and r rotations based on the maximum velocity characterized
        """
        veloc_x = x * self.maxVelocity.get()
        veloc_y = y * self.maxVelocity.get()
        veloc_r = r * self.maxAngularVelocity.get()

        if self.isFieldRelative():
            speeds = ChassisSpeeds.fromFieldRelativeSpeeds(
                vx = veloc_x,
                vy = veloc_y,
                omega = veloc_r, # radians per second
                robotAngle = self.getRobotAngle()
            )
        else:
            speeds = ChassisSpeeds(
                vx = veloc_x,
                vy = veloc_y,
                omega = veloc_r
            )

        # Send ChassisSpeeds
        self.runChassisSpeeds(speeds)

    def runChassisSpeeds(self, speeds:ChassisSpeeds, convertToFieldRelative:bool = False) -> None:
        """
        Runs this SwerveDrive based on the provided ChassisSpeed
        """
        if convertToFieldRelative: speeds = ChassisSpeeds.fromRobotRelativeSpeeds( speeds, self.getRobotAngle() ) # Needed for Trajectory State not being field relative
        modStates = self.getKinematics().toSwerveModuleStates(speeds, Translation2d(0, 0)) # Convert to SwerveModuleState
        self.runSwerveModuleStates( modStates )

    def runSwerveModuleStates(self, states:typing.Tuple[ SwerveModuleState,
                                                         SwerveModuleState,
                                                         SwerveModuleState,
                                                         SwerveModuleState ]) -> None:
        """
        Runs this SwerveDrive based on provided SwerveModuleState.

        This method will optomize the SwerveModuleState prior to use to minimize the turning to less than 90 degrees
        """
        # Update Desired State for each Swerve Module
        optStates = SwerveDrive4Kinematics.desaturateWheelSpeeds(states, self.maxVelocity.get())
        for x in range(len(self.modules)):
            optimalState:SwerveModuleState = SwerveModuleState.optimize(
                optStates[x],
                self.modules[x].getModulePosition().angle
            )
            self.modules[x].setModuleState( optimalState )
