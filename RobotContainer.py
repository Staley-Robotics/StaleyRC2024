import typing

import commands2
import commands2.button
import commands2.cmd
import wpilib
import wpimath
from wpilib.interfaces import GenericHID

from subsystems import *
from commands import *
from sequences import *
from autonomous import *
from util import *

#NOTE: swerve sections commented out for other prototyping
class RobotContainer:
    """
    Constructs a RobotContainer for the {Game}
    """
    testing:bool = False

    def __init__(self):
        """
        Initialization
        """
        ### Tunable Variables
        self.endgameTimer1 = NTTunableFloat( "/Config/Game/EndGameNotifications/1", 30.0 )
        self.endgameTimer2 = NTTunableFloat( "/Config/Game/EndGameNotifications/2", 15.0 )
        self.notifier = NTTunableBoolean( "/Logging/Game/EndGameNotifications", False )

        # Create Subsystems
        # IO Systems
        ssModulesIO = None
        ssGyroIO = None
        ssCamerasIO = None
        ssIndexerIO = None
        ssIntakeIO = None
        ssLauncherIO = None
        ssPivotIO = None
        ssElevatorIO = None
        #ssLedIO = None

        # Create IO Systems
        if wpilib.RobotBase.isSimulation() and not self.testing:
            ssModulesIO = [
                SwerveModuleIOSim("FL",  0.25,  0.25 ), 
                SwerveModuleIOSim("FR",  0.25, -0.25 ), 
                SwerveModuleIOSim("BL", -0.25,  0.25 ),
                SwerveModuleIOSim("BR", -0.25, -0.25 ) 
            ]
            ssGyroIO = GyroIOPigeon2( 9, 0 )
            ssIntakeIO = IntakeIOSim()
            ssIndexerIO = IndexerIOSim()
            ssLauncherIO = LauncherIOSim()
            ssPivotIO = PivotIOSim()
            #ssElevatorIO = ElevatorIOSim()
            ssLedIO = LedIOSim( 9 )
        else:
            ssModulesIO = [
                SwerveModuleIONeo("FL", 7, 8, 18,  0.25,  0.25,  97.471 ), #211.289)
                SwerveModuleIONeo("FR", 1, 2, 12,  0.25, -0.25,  5.361 ), #125.068) #  35.684)
                SwerveModuleIONeo("BL", 5, 6, 16, -0.25,  0.25,  298.828 ), #223.945)
                SwerveModuleIONeo("BR", 3, 4, 14, -0.25, -0.25,  60.557 )  #65.654)
            ]
            ssGyroIO = GyroIOPigeon2( 9, 0 )
            ssIntakeIO = IntakeIOFalcon( 20, 21, 0 )
            ssIndexerIO = IndexerIONeo( 22, 1, 2 )
            ssLauncherIO = LauncherIONeo( 23, 24 , 3)
            ssPivotIO = PivotIOFalcon( 25, 26, -48.691 )
            #ssElevatorIO = ElevatorIONeo( 27, 28 )
            ssLedIO = LedIOActual( 0 )

        Vision
        ssCamerasIO:typing.Tuple[VisionCamera] = [
            VisionCameraLimelight( "limelight-one" ),
            VisionCameraLimelight( "limelight-two" )
        ]

        # Link IO Systems to Subsystems
        self.drivetrain:SwerveDrive = SwerveDrive( ssModulesIO, ssGyroIO )
        self.intake:Intake = Intake( ssIntakeIO )
        self.feeder:Indexer = Indexer( ssIndexerIO )
        self.launcher:Launcher = Launcher( ssLauncherIO )
        self.pivot:Pivot = Pivot( ssPivotIO )
        #self.elevator:Elevator = Elevator( ssElevatorIO )
        # self.vision = Vision( ssCamerasIO, self.drivetrain.getOdometry )
        self.led = LED( ssLedIO )

        # Add Subsystems to SmartDashboard
        wpilib.SmartDashboard.putData( "SwerveDrive", self.drivetrain )
        wpilib.SmartDashboard.putData( "Intake", self.intake )
        wpilib.SmartDashboard.putData( "Indexer", self.feeder )
        wpilib.SmartDashboard.putData( "Launcher", self.launcher )
        wpilib.SmartDashboard.putData( "Pivot", self.pivot )
        #wpilib.SmartDashboard.putData( "Elevator", self.elevator )
        wpilib.SmartDashboard.putData( "LED", self.led )

        # Add Commands to SmartDashboard
        wpilib.SmartDashboard.putData( "Zero Odometry", commands.cmd.runOnce( self.drivetrain.resetOdometry ).ignoringDisable(True) )
        wpilib.SmartDashboard.putData( "Sync Gyro to Pose", commands.cmd.runOnce( self.drivetrain.syncGyro ).ignoringDisable(True) )
        wpilib.SmartDashboard.putData( "run led rainbow", runLedRainbow(self.led))

        # Add Commands to SmartDashboard
        #nothing rn

        # Configure Driver 1 Button Mappings
        self.m_driver1 = commands2.button.CommandXboxController(0)
        ## Driving
        # self.m_driver1.a().toggleOnTrue( DemoSwerveDriveTimedPath( self.drivetrain ) )
        # self.m_driver1.b().toggleOnTrue( DemoSwerveDrivePoses( self.drivetrain ) )
        # self.m_driver1.x().onTrue( DriveDistance( self.drivetrain, distance = lambda: Pose2d( 2, 0, Rotation2d(0) ) ) )
        # self.m_driver1.y().onTrue( DriveDistance( self.drivetrain, distance = lambda: Pose2d( 0, 2, Rotation2d(0) ) ) ) 
        self.m_driver1.rightBumper().whileTrue(
            commands.DriveAimSpeaker(
                self.drivetrain,
                self.m_driver1.getLeftY,
                self.m_driver1.getLeftX
            )
        )

        ## Mechanisms
        #Intake
        # self.m_driver1.y().whileTrue( IntakeLoad( self.intake ) )
        # self.m_driver1.x().whileTrue( IntakeHandoff( self.intake ) )
        # # self.m_driver1.x().whileTrue( IntakeEject( self.intake ) )
        # #Indexer
        # self.m_driver1.b().whileTrue( IndexerHandoff( self.feeder ))
        # #Launcher
        # self.m_driver1.a().whileTrue( LauncherSpeaker( self.launcher ))

        # self.m_driver1.a().onTrue( PivotToPosition(self.pivot, Pivot.PivotPositions.Handoff.get) )
        # self.m_driver1.b().onTrue( PivotToPosition(self.pivot, Pivot.PivotPositions.Source.get) )
        # self.m_driver1.x().onTrue( PivotToPosition(self.pivot, Pivot.PivotPositions.Upward.get) )

        # self.m_driver1.a().whileTrue( runLedRainbow(self.led) )


        # Configure Driver 2 Button Mappings
        #self.m_driver2 = commands2.button.CommandXboxController(1)
        #self.m_driver2.a().whileTrue( sequences.SampleSequence() )

        # End Game Notifications
        self.setEndgameNotification( self.endgameTimer1.get, 1.0, 1, 0.5 ) # First Notice
        self.setEndgameNotification( self.endgameTimer2.get, 0.5, 2, 0.5 ) # Second Notice

        # Configure Default Commands
        self.drivetrain.setDefaultCommand(
            commands.DriveByStick(
                self.drivetrain,
                self.m_driver1.getLeftY,
                self.m_driver1.getLeftX,
                self.m_driver1.getRightY,
                self.m_driver1.getRightX,
                lambda: self.m_driver1.getLeftTriggerAxis() - self.m_driver1.getRightTriggerAxis()
            )
        )
        # self.pivot.setDefaultCommand(
        #     commands.PivotByStick(
        #         self.pivot,
        #         self.m_driver1.getLeftY
        #     )
        # )
    
    def setEndgameNotification( self,
                                getAlertTime:typing.Callable[[],float],
                                rumbleTime:float = 1.0,
                                pulseCount:int = 1,
                                pulseDelay:float = 0.5 ) -> None:
        """
        Creates a Customizable End Game Notification and adds is to the Command Scheduler
        
        :param getAlertTime: A lambda function that requests the amount of time (in seconds)
        remaining in the match when the notification occurs
        :param rumbleTime: The amount of time (in seconds) the rumble occurs
        :param pulseCount: The number of times (pulses) the notification occurs
        :param pulseDelay: The amount of time (in seconds) to delay between notification pulses
        """
        # Create Rumble Patterns
        rumbleSequence = commands2.cmd.sequence()
        for i in range(pulseCount):
            # Start Rumble
            rumbleSequence = rumbleSequence.andThen(
                commands2.cmd.run(
                    lambda: (
                        self.m_driver1.getHID().setRumble( GenericHID.RumbleType.kBothRumble, 1.0 ),
                        #self.m_driver2.getHID().setRumble( GenericHID.RumbleType.kBothRumble, 1.0 ),
                        self.notifier.set( True ) # Visualization on Dashboard
                    )
                ).withTimeout( rumbleTime )
            )
            # Stop Rumble
            rumbleSequence = rumbleSequence.andThen(
                commands2.cmd.run(
                    lambda: (
                        self.m_driver1.getHID().setRumble( GenericHID.RumbleType.kBothRumble, 0.0 ),
                        #self.m_driver2.getHID().setRumble( GenericHID.RumbleType.kBothRumble, 0.0 ),
                        self.notifier.set( False ) # Visualization on Dashboard
                    )
                ).withTimeout( pulseDelay )
            )

        # Bind Rumble Triggers to 
        commands2.button.Trigger(
            lambda: ( DriverStation.isTeleopEnabled() 
                and DriverStation.getMatchTime() > 0.0 
                and DriverStation.getMatchTime() <= round( getAlertTime(), 2 )
            )
        ).onTrue( rumbleSequence )
