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
        # Tunable Variables
        self.endgameTimer1 = NTTunableFloat( "/Config/Game/EndGameNotifications/1", 30.0 )
        self.endgameTimer2 = NTTunableFloat( "/Config/Game/EndGameNotifications/2", 15.0 )
        self.notifier = NTTunableBoolean( "/Logging/Game/EndGameNotifications", False )

        # Create Subsystems
        #self.launcher = LauncherSparkMaxWFeed() #TODO: split to use indexer subsystem and independant launcher
        #self.indexer = Index
        self.intake = IntakeTalon_FX()
        #self.pivot = PivotIOTalon()

        '''IR?'''
        # self.irSensor = DigitalInput(0)
        # self.irEmitter = DigitalOutput(1)


        # Add Subsystems to SmartDashboard
        #wpilib.SmartDashboard.putData( "Launcher", self.launcher)
        #wpilib.SmartDashboard.putData('pivot', self.pivot)

        # Add Commands to SmartDashboard
        #wpilib.SmartDashboard.putData( "Launcher Running", commands.RunLauncher(self.launcher) )

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
    
