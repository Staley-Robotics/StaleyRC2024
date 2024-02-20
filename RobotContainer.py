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

        ### Create Subsystems
        # IO Systems
        ssModulesIO = None
        ssGyroIO = None
        ssCamerasIO = None
        ssIntakeIO = None
        ssIndexerIO = None
        ssLauncherIO = None
        ssPivotIO = None
        ssElevatorIO = None

        # Create IO Systems
        if wpilib.RobotBase.isSimulation() and not self.testing:
            ssModulesIO = [
                SwerveModuleIOSim("FL",  0.25,  0.25 ), 
                SwerveModuleIOSim("FR",  0.25, -0.25 ), 
                SwerveModuleIOSim("BL", -0.25,  0.25 ),
                SwerveModuleIOSim("BR", -0.25, -0.25 ) 
            ]
            ssGyroIO = GyroIOPigeon2( 10, 0 )
            ssIntakeIO = IntakeIOSim()
            ssIndexerIO = IndexerIOSim()
            ssLauncherIO = LauncherIOSim()
            ssPivotIO = PivotIOSim()
            ssElevatorIO = ElevatorIOSim()
        else:
            ssModulesIO = [
                SwerveModuleIONeo("FL", 7, 8, 18,  0.25,  0.25,  96.837 ), #211.289)
                SwerveModuleIONeo("FR", 1, 2, 12,  0.25, -0.25,   6.240 ), #125.068) #  35.684)
                SwerveModuleIONeo("BL", 5, 6, 16, -0.25,  0.25, 299.954 ), #223.945)
                SwerveModuleIONeo("BR", 3, 4, 14, -0.25, -0.25,  60.293 )  #65.654)
            ]
            ssGyroIO = GyroIOPigeon2( 10, 0 )
            ssIntakeIO = IntakeIOFalcon( 3, 4, 0 )
            ssIndexerIO = IndexerIONeo( 16, 1, 2 )
            ssLauncherIO = LauncherIONeo( 20, 9 , 3)
            ssPivotIO = PivotIOFalcon( 15, 10, 0.0 )
            ssElevatorIO = ElevatorIONeo( 21, 22 )

        # Vision
        ssCamerasIO:typing.Tuple[VisionCamera] = [
            VisionCameraLimelight( "limelight-one" ),
            VisionCameraLimelight( "limelight-two" )
        ]

        # Link IO Systems to Subsystems
        self.drivetrain:SwerveDrive = SwerveDrive( ssModulesIO, ssGyroIO )
        self.intake:Intake = Intake( ssIntakeIO )
        self.indexer:Indexer = Indexer( ssIndexerIO )
        self.launcher:Launcher = Launcher( ssLauncherIO )
        self.pivot:Pivot = Pivot( ssPivotIO )
        self.elevator:Elevator = Elevator( ssElevatorIO )
        self.vision = Vision( ssCamerasIO, self.drivetrain.getOdometry )

        # Add Subsystems to SmartDashboard
        wpilib.SmartDashboard.putData( "SwerveDrive", self.drivetrain )
        wpilib.SmartDashboard.putData( "Intake", self.intake )
        wpilib.SmartDashboard.putData( "Indexer", self.indexer )
        wpilib.SmartDashboard.putData( "Launcher", self.launcher )
        wpilib.SmartDashboard.putData( "Pivot", self.pivot )
        wpilib.SmartDashboard.putData( "Elevator", self.elevator )

        # Add Commands to SmartDashboard
        wpilib.SmartDashboard.putData( "Command", SampleCommand1() )
        wpilib.SmartDashboard.putData( "Zero Odometry", commands.cmd.runOnce( self.drivetrain.resetOdometry ).ignoringDisable(True) )
        wpilib.SmartDashboard.putData( "Sync Gyro to Pose", commands.cmd.runOnce( self.drivetrain.syncGyro ).ignoringDisable(True) )

        # Add Commands to SmartDashboard
        #nothing rn

        # Configure Driver 1 Button Mappings
        self.m_driver1 = commands2.button.CommandXboxController(0)
        # # B button go brrrr
        # self.m_driver1.b().whileTrue( commands.RunLauncher(self.launcher) )
        # # change launcher speeds
        # self.m_driver1.leftBumper().whileTrue(commands.DecrementLauncherSpeed(self.launcher))
        # self.m_driver1.rightBumper().whileTrue(commands.IncrementLauncherSpeed(self.launcher))
        # # run feeder
        # self.m_driver1.y().whileTrue(commands.RunFeeder(self.launcher))
        # self.m_driver1.x().whileTrue(commands.RunFeederReversed(self.launcher))
        # #run intake
        # self.m_driver1.a().whileTrue(commands.RunIntake(self.intake))
        # self.m_driver1.a().onTrue(commands.EnableEmitter(self.irEmitter))
        # self.m_driver1.b().onTrue(commands.EnableEmitter(self.irEmitter))

        # self.m_driver1.x().whileTrue(commands.printReciever(self.irSensor))

    
        #default commands
        # self.pivot.setDefaultCommand(
        #     commands.PointPivotToAngle(
        #         self.pivot,
        #         self.m_driver1.getLeftTriggerAxis,
        #         self.m_driver1.getRightTriggerAxis
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
