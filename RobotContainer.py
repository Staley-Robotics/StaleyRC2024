import typing

import commands2
import commands2.button
import commands2.cmd
import wpilib
import wpilib.shuffleboard
from wpilib.interfaces import GenericHID

from subsystems import *
from commands import *
from sequences import *
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
        self.endgameTimer1 = NTTunableFloat( "/Config/Game/EndGameNotifications/1", 30.0, persistent=True )
        self.endgameTimer2 = NTTunableFloat( "/Config/Game/EndGameNotifications/2", 15.0, persistent=True )
       
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
        ssLedIO = None
        ssClimberIOLeft = None
        ssClimberIORight = None
        ppCommands = {}

        # Create IO Systems
        if wpilib.RobotBase.isSimulation() and not self.testing:
            ssModulesIO = [
                SwerveModuleIOSim("FL",  0.25,  0.25 ), 
                SwerveModuleIOSim("FR",  0.25, -0.25 ), 
                SwerveModuleIOSim("BL", -0.25,  0.25 ),
                SwerveModuleIOSim("BR", -0.25, -0.25 ) 
            ]
            ssGyroIO = GyroIOPigeon2( 9 )
            ssIntakeIO = IntakeIOSim()
            ssIndexerIO = IndexerIOSim()
            ssLauncherIO = LauncherIOSim()
            ssPivotIO = PivotIOSim()
            ssLedIO = Led2IOPwm( 0 )
            ssClimberIOLeft = ClimberIO()
            ssClimberIORight = ClimberIO()
        else:
            if wpilib.RobotBase.isSimulation():
                ssModulesIO = [
                    SwerveModuleIOSim("FL",  0.25,  0.25 ), 
                    SwerveModuleIOSim("FR",  0.25, -0.25 ), 
                    SwerveModuleIOSim("BL", -0.25,  0.25 ),
                    SwerveModuleIOSim("BR", -0.25, -0.25 ) 
                ]
            else:
                ssModulesIO = [
                    SwerveModuleIONeo("FL", 7, 8, 18,  0.2667,  0.2667,  97.471 ), #211.289)
                    SwerveModuleIONeo("FR", 1, 2, 12,  0.2667, -0.2667,  5.361 ), #125.068) #  35.684)
                    SwerveModuleIONeo("BL", 5, 6, 16, -0.2667,  0.2667,  298.828 ), #223.945)
                    SwerveModuleIONeo("BR", 3, 4, 14, -0.2667, -0.2667,  60.557 )  #65.654)
                ]
            ssGyroIO = GyroIOPigeon2( 9 )
            ssIntakeIO = IntakeIOFalcon( 20, 21, 0, 9 )
            ssIndexerIO = IndexerIONeo( 22, 2, 1 )
            ssLauncherIO = LauncherIOFalcon( 23, 24 , 3 )
            ssPivotIO = PivotIOFalcon( 25, 26, -77.520+1.318 )
            ssLedIO = Led2IOPwm( 0 )
            ssClimberIOLeft = ClimberIOTalon( 27, 5, 6 )
            ssClimberIORight = ClimberIOTalon( 28, 7, 8, True )

        # Vision
        ssCamerasIO:typing.Tuple[VisionCamera] = [
            VisionCameraLimelight3( "limelight-one" ),
            VisionCameraLimelight3( "limelight-two" ),
            VisionCameraLimelight3( "limelight-three" ),
            VisionCameraLimelight3( "limelight-four" )
        ]

        # Link IO Systems to Subsystems
        self.drivetrain:SwerveDrive = SwerveDrive( ssModulesIO, ssGyroIO )
        self.vision = Vision( ssCamerasIO, self.drivetrain.getOdometry )
        self.intake:Intake = Intake( ssIntakeIO )
        self.feeder:Indexer = Indexer( ssIndexerIO )
        self.pivot:Pivot = Pivot( ssPivotIO )
        self.launcher:Launcher = Launcher( ssLauncherIO )
        self.climber = Climber( ssClimberIOLeft, ssClimberIORight )
        self.launchCalc = LaunchCalc( self.drivetrain.getPose )
        self.led = Led2( ssLedIO )

        # Register Pathplanner Commands
        if wpilib.RobotBase.isSimulation():
            ppCommands = {
                "AutoPivot": commands2.cmd.waitSeconds( 0.50 ),
                "AutoLaunch": commands2.cmd.waitSeconds( 0.50 ).andThen(commands2.cmd.runOnce( lambda: self.feeder.setHasNote(False) )),
                "AutoPickup": commands2.cmd.waitSeconds( 0.50 ).andThen(commands2.cmd.runOnce( lambda: self.feeder.setHasNote(True) ))
            }
        else:
            ppCommands = {
                "AutoPivot": PivotAim(self.pivot, self.launchCalc.getLaunchAngle),
                "AutoLaunch": NoteLaunchSpeakerAuto(self.feeder, self.launcher, self.pivot, self.launchCalc),
                "AutoPickup": NoteLoadGround(self.intake, self.feeder, self.pivot)
            }
        self.pathPlanner = SwervePath( self.drivetrain, self.launchCalc.getRotateAngle, self.feeder.hasNote )   
        self.pathPlanner.setNamedCommands( ppCommands )

        # Add Subsystems to SmartDashboard
        wpilib.SmartDashboard.putData( "SwerveDrive", self.drivetrain )
        wpilib.SmartDashboard.putData( "Intake", self.intake )
        wpilib.SmartDashboard.putData( "Indexer", self.feeder )
        wpilib.SmartDashboard.putData( "Pivot", self.pivot )
        wpilib.SmartDashboard.putData( "Launcher", self.launcher )
        wpilib.SmartDashboard.putData( "Climber", self.climber )
        wpilib.SmartDashboard.putData( "LED", self.led )

        # Add Commands to SmartDashboard
        wpilib.SmartDashboard.putData( "Zero Odometry", commands2.cmd.runOnce( self.drivetrain.resetOdometry ).ignoringDisable(True) )
        wpilib.SmartDashboard.putData( "Set Gyro Offset", commands2.cmd.runOnce( self.drivetrain.syncGyro ).ignoringDisable(True) )
        wpilib.SmartDashboard.putData( "LauncherSpeaker", LauncherSpeaker(self.launcher) )
        wpilib.SmartDashboard.putData( "LedButton", LedAction(self.led))

        # Configure and Add Autonomous Mode to SmartDashboard
        self.m_chooser = wpilib.SendableChooser()
        self.m_chooser.setDefaultOption("1 - None", commands2.cmd.none() )
        self.pathPlanner.updatePathPlannerAutoList( self.m_chooser )
        wpilib.SmartDashboard.putData("Autonomous Mode", self.m_chooser)

        # Configure Driver 1 Button Mappings
        self.m_driver1 = commands2.button.CommandXboxController(0)
        self.m_driver2 = commands2.button.CommandXboxController(1)
        self.station = wpilib.Joystick(2)
        self.stationCmd = commands2.button.CommandJoystick(2)

        # Operator Switches
        if RobotBase.isSimulation():
            self.swIntakeAuto:bool = False
            self.swLaunchSpinAuto:bool = False
            self.swPivotAuto:bool = False
            self.swPivotManual:bool = False
            self.swClimb:bool = False

            def getSwitchIntakeAuto() -> bool: return self.swIntakeAuto
            def getSwitchPivotAuto() -> bool: return self.swPivotAuto
            def getSwitchPivotManual() -> bool: return self.swPivotManual 
            def getSwitchLaunchSpinAuto() -> bool: return self.swLaunchSpinAuto
            def getSwitchClimb() -> bool: return self.swClimb

            def updateNtLogging():
                ntTbl = NetworkTableInstance.getDefault().getTable("/Logging/Switches")
                ntTbl.putBoolean( "IntakeAuto", getSwitchIntakeAuto() )
                ntTbl.putBoolean( "PivotAuto", getSwitchPivotAuto() )
                ntTbl.putBoolean( "PivotManual", getSwitchPivotManual() )
                ntTbl.putBoolean( "LaunchSpinAuto", getSwitchLaunchSpinAuto() )
                ntTbl.putBoolean( "Climb", getSwitchClimb() )
            
            def toggleSwitchIntakeAuto(): self.swIntakeAuto = not self.swIntakeAuto; updateNtLogging()
            def toggleSwitchLaunchSpinAuto(): self.swLaunchSpinAuto = not self.swLaunchSpinAuto; updateNtLogging()
            def toggleSwitchPivotAuto(): self.swPivotAuto = not self.swPivotAuto; updateNtLogging()
            def toggleSwitchPivotManual(): self.swPivotManual = not self.swPivotManual; updateNtLogging()
            def toggleSwitchClimb(): self.swClimb = not self.swClimb; updateNtLogging()

            updateNtLogging()
            self.stationCmd.button(5).onTrue( commands2.cmd.runOnce( toggleSwitchIntakeAuto ).ignoringDisable(True) )
            self.stationCmd.button(6).onTrue( commands2.cmd.runOnce( toggleSwitchLaunchSpinAuto ).ignoringDisable(True) )
            self.stationCmd.button(7).onTrue( commands2.cmd.runOnce( toggleSwitchPivotAuto ).ignoringDisable(True) )
            self.stationCmd.button(8).onTrue( commands2.cmd.runOnce( toggleSwitchPivotManual ).ignoringDisable(True) )
            self.stationCmd.button(9).onTrue( commands2.cmd.runOnce( toggleSwitchClimb ).ignoringDisable(True) )
        else:
            def getSwitchIntakeAuto() -> bool: return self.station.getRawButton(5)
            def getSwitchLaunchSpinAuto() -> bool: return self.station.getRawButton(6)
            def getSwitchPivotAuto() -> bool: return self.station.getRawButton(7)
            def getSwitchPivotManual() -> bool: return self.station.getRawButton(8)
            def getSwitchClimb() -> bool: return self.station.getRawButton(9)
        
        ## Controller Configs
        self.m_driver1.a().whileTrue( DriveFlyByPath( self.drivetrain, self.feeder.hasNote, self.launchCalc.getTarget, getSwitchPivotAuto ) ) # Drive - FlyByPath
        self.m_driver1.b().onTrue(
            commands2.cmd.runOnce(
                lambda: self.launchCalc.setTarget( LaunchCalc.Targets.AMP if self.launchCalc.getTarget() == LaunchCalc.Targets.SPEAKER else LaunchCalc.Targets.SPEAKER )
            ).ignoringDisable(True)
        ) # Toggle Target
        self.m_driver1.x().toggleOnTrue( NoteAction( self.intake, self.feeder, self.launcher, self.pivot, self.launchCalc ) ) # NoteAction:  NoteLoadGround, NoteLaunchSpeaker, NoteLaunchAmp, NoteLaunchToss
        self.m_driver1.leftBumper().whileTrue( ClimberExtend( self.climber ) )
        self.m_driver1.rightBumper().onTrue( ToggleHalfSpeed() )  # Toggle Half Speed
        self.m_driver1.back().onTrue( ToggleFieldRelative() ) # Toggle Field Relative
        self.m_driver1.start().onTrue( commands2.cmd.runOnce( self.drivetrain.syncGyro ).ignoringDisable(True) ) # Resync Gyro - Do we need this?
        
        #  Driver 2
        self.m_driver2.a().whileTrue( DriveAim( self.drivetrain, self.m_driver1.getLeftY, self.m_driver1.getLeftX, self.launchCalc.getTarget ) ) # Drive - Force Aiming
        self.m_driver2.x().toggleOnTrue( NoteAction( self.intake, self.feeder, self.launcher, self.pivot, self.launchCalc ) ) # NoteAction: NoteLoadGround, NoteLaunchSpeaker, NoteLaunchAmp, NoteLaunchToss
        self.m_driver2.b().whileTrue( AllRealign( self.intake, self.feeder, self.launcher, self.pivot ) ) # Realign Pivot with Intake
        self.m_driver2.y().whileTrue( PivotBottom( self.pivot ) ) # Pivot Down
        #self.m_driver2.leftBumper().onTrue( NoteLaunchAmp( self.feeder, self.launcher, self.pivot ) ) 
        self.m_driver2.rightBumper().onTrue( AllStop( self.intake, self.feeder, self.launcher, self.pivot ) )
        self.m_driver2.start().onTrue( EjectAll( self.intake, self.feeder, self.launcher, self.pivot ) )

        self.m_driver2.povUp().onTrue(
            commands2.cmd.runOnce( lambda: self.launchCalc.modifyAimAdjust( 0.5 ) ).ignoringDisable(True)
        )
        self.m_driver2.povDown().onTrue(
            commands2.cmd.runOnce( lambda: self.launchCalc.modifyAimAdjust( -0.5 ) ).ignoringDisable(True)
        )
        
        # Operator Station Buttons 
        #self.stationCmd.button(6).whileTrue( NoteLoadGround( self.intake, self.feeder, self.pivot ) )
        self.stationCmd.button(12).toggleOnTrue( IntakeLoad(self.intake).onlyIf( lambda: not self.feeder.hasNote() ) ) # whileTrue( IntakeLoad( self.intake ) )
        self.stationCmd.button(11).whileTrue( NoteLoadSource( self.feeder, self.pivot, self.launcher ) )
        self.stationCmd.button(2).whileTrue( NoteToss( self.feeder, self.launcher, self.pivot ) )
        self.stationCmd.button(1).whileTrue( NoteLaunchSpeaker( self.feeder, self.launcher, self.pivot, self.launchCalc ) )
        self.stationCmd.button(10).whileTrue( EjectAll( self.intake, self.feeder, self.launcher, self.pivot ) )
        self.stationCmd.button(3).whileTrue( AllStop( self.intake, self.feeder, self.launcher, self.pivot ) )
        self.stationCmd.button(4).whileTrue( LedAction(self.led) )

        # Configure Default Commands (with Operatory Station Toggles integrated)
        self.drivetrain.setDefaultCommand(
            DriveByStick(
                self.drivetrain,
                self.m_driver1.getLeftY,
                self.m_driver1.getLeftX,
                self.m_driver1.getRightY,
                self.m_driver1.getRightX,
                lambda: self.m_driver1.getLeftTriggerAxis() - self.m_driver1.getRightTriggerAxis()
            )
        )
        self.intake.setDefaultCommand(
            IntakeDefault(
                self.intake,
                self.feeder.hasNote,
                self.pivot.atSetpoint,
                useAutoStart = getSwitchIntakeAuto
            )
        )
        self.pivot.setDefaultCommand(
            PivotDefault(
                self.pivot,
                self.feeder.hasNote,
                self.launchCalc.getLaunchAngle,
                self.m_driver2.getLeftY,
                isTargetAmp = self.launchCalc.isTargetAmp,
                isIntakeWaiting = self.intake.isWaiting,
                useAutoCalculate = getSwitchPivotAuto,
                useManualAdjust = getSwitchPivotManual
            )
        )
        self.feeder.setDefaultCommand(
            IndexerDefault(
                self.feeder,
                self.intake.hasNote,
                self.pivot.atSetpoint,
                self.launchCalc.isAutoLaunchApproved
            )
        )
        self.launcher.setDefaultCommand(
            LauncherDefault(
                self.launcher,
                self.launchCalc.getDistance,
                self.feeder.hasNote,
                isTargetAmp = self.launchCalc.isTargetAmp,
                useAutoStart = getSwitchLaunchSpinAuto
            )
        )
        self.climber.setDefaultCommand(
            ClimberDefault(
                self.climber,
                lambda: self.station.getRawAxis(1),
                getSwitchClimb
            )
        )

        # LED Configuration
        self.led.setIntakeIsRunning( self.intake.isRunning )
        self.led.setIntakeHasNote( self.intake.hasNote )
        self.led.setIndexerHasNote( self.feeder.hasNote )
        self.led.setPivotAutoAdjust( getSwitchPivotAuto )
        self.led.setPivotAtSetpoint( self.pivot.atSetpoint )
        self.led.setLaunchRotation( self.launchCalc.inRotationRange )
        self.led.setLaunchRangeFar( self.launchCalc.inFarRange )
        self.led.setLaunchRangeNear( self.launchCalc.inNearRange )
        self.led.setLaunchRangeAuto( self.launchCalc.inAutoRange )
        self.led.setIsEndgame( self.notifier.get )

        # End Game Notifications
        self.setEndgameNotification( self.endgameTimer1.get, 1.0, 1, 0.5 ) # First Notice
        self.setEndgameNotification( self.endgameTimer2.get, 0.5, 2, 0.5 ) # Second Notice

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
                        self.m_driver2.getHID().setRumble( GenericHID.RumbleType.kBothRumble, 1.0 ),
                        self.notifier.set( True ) # Visualization on Dashboard
                    )
                ).withTimeout( rumbleTime )
            )
            # Stop Rumble
            rumbleSequence = rumbleSequence.andThen(
                commands2.cmd.run(
                    lambda: (
                        self.m_driver1.getHID().setRumble( GenericHID.RumbleType.kBothRumble, 0.0 ),
                        self.m_driver2.getHID().setRumble( GenericHID.RumbleType.kBothRumble, 0.0 ),
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

    def getAutonomousCommand(self) -> commands2.Command:
        """
        :returns: the autonomous command that has been selected from the ShuffleBoard
        """
        return self.m_chooser.getSelected()

    def runCalibration(self) -> None:
        """
        Adds the calibration commands to the Command Scheduler
        """
        self.drivetrain.syncGyro()
        

