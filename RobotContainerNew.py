import commands2
import commands2.button
import commands2.cmd
import wpilib
from wpilib.interfaces import GenericHID

from subsystems import *
from commands import *
from sequences import *
from autonomous import *
from util import *

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
        modulesIO = None
        gyroIO = None
        camerasIO = None
        intakeIO = None
        indexerIO = None
        launcherIO = None
        pivotIO = None
        elevatorIO = None

        # Create IO Systems
        if wpilib.RobotBase.isSimulation() and not self.testing:
            modulesIO = [
                SwerveModuleSim("FL",  0.25,  0.25 ), 
                SwerveModuleSim("FR",  0.25, -0.25 ), 
                SwerveModuleSim("BL", -0.25,  0.25 ),
                SwerveModuleSim("BR", -0.25, -0.25 ) 
            ]
            gyroIO = GyroPigeon2( 10, "rio", 0 )
            intakeIO = IntakeIOSim()
            indexerIO = IndexerIOSim()
            launcherIO = LauncherIOSim()
            pivotIO = PivotIOSim()
            elevatorIO = ElevatorIOSim()
        else:
            modulesIO = [
                SwerveModuleNeo("FL", 7, 8, 18,  0.25,  0.25,  96.837 ), #211.289)
                SwerveModuleNeo("FR", 1, 2, 12,  0.25, -0.25,   6.240 ), #125.068) #  35.684)
                SwerveModuleNeo("BL", 5, 6, 16, -0.25,  0.25, 299.954 ), #223.945)
                SwerveModuleNeo("BR", 3, 4, 14, -0.25, -0.25,  60.293 )  #65.654)
            ]
            gyroIO = GyroPigeon2( 10, "rio", 0 )
            intakeIO = IntakeIOFalcon( 3, 4 )
            indexerIO = IndexerIONeo( 16 )
            launcherIO = LauncherIONeo( 20, 9 )
            pivotIO = PivotIOFalcon( 15, 10 )
            elevatorIO = ElevatorIONeo( 21, 22 )

        # Vision
        camerasIO:typing.Tuple[VisionCamera] = [
            VisionCameraLimelight( "limelight-one" ),
            VisionCameraLimelight( "limelight-two" )
        ]

        # Link IO Systems to Subsystems
        self.drivetrain:SwerveDrive = SwerveDrive( modulesIO, gyroIO )
        self.intake:Intake = Intake( intakeIO )
        self.indexer:Indexer = Indexer( indexerIO )
        self.launcher:Launcher = Launcher( launcherIO )
        self.pivot:Pivot = Pivot( pivotIO )
        self.elevator:Elevator = Elevator( elevatorIO )
        self.vision = Vision( camerasIO, self.drivetrain.getOdometry )

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

        # Configure and Add Autonomous Mode to SmartDashboard
        self.m_chooser = wpilib.SendableChooser()
        self.m_chooser.setDefaultOption("1 - None", commands2.cmd.none() )
        self.m_chooser.addOption("2 - DriveCharacterization", DriveCharacterization( self.drivetrain, True, 1.0 ) )
        self.m_chooser.addOption("3 - Drive Under Stage", AutoUnderStage( self.drivetrain ) )
        self.m_chooser.addOption("4 - Drive Under Stage (PP)", AutoUnderStagePP( self.drivetrain ) )
        self.m_chooser.addOption("5 - Autonomous Command", SampleAuto1() )
        wpilib.SmartDashboard.putData("Autonomous Mode", self.m_chooser)
        
        # Configure Driver 1 Button Mappings
        self.m_driver1 = commands2.button.CommandXboxController(0)
        self.m_driver1.a().toggleOnTrue( DemoSwerveDriveTimedPath( self.drivetrain ) )
        self.m_driver1.b().toggleOnTrue( DemoSwerveDrivePoses( self.drivetrain ) )
        self.m_driver1.x().onTrue( DriveDistance( self.drivetrain, distance = lambda: Pose2d( 2, 0, Rotation2d(0) ) ) )
        self.m_driver1.y().onTrue( DriveDistance( self.drivetrain, distance = lambda: Pose2d( 0, 2, Rotation2d(0) ) ) ) 

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
        self.pivot.setDefaultCommand(
            commands.RunPivotOpenLoop(
            self.pivot,
            self.m_driver1.getRightTriggerAxis,
            self.m_driver1.getLeftTriggerAxis
            )
        )

    def getAutonomousCommand(self) -> commands2.Command:
        """
        :returns: the autonomous command that has been selected from the ShuffleBoard
        """
        return self.m_chooser.getSelected()
    
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