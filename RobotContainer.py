import commands2
import commands2.button
import commands2.cmd
import wpilib

import subsystems
import commands
import sequences
import autonomous
import util

class RobotContainer:
    """
    Constructs a RobotContainer for the {Game}
    """

    def __init__(self):
        """
        
        """
        # Create Subsystems
        self.launcher = subsystems.Launcher()

        # Add Subsystems to SmartDashboard
        wpilib.SmartDashboard.putData( "Launcher", self.launcher)

        # Add Commands to SmartDashboard
        wpilib.SmartDashboard.putData( "Launcher Running", commands.RunLauncher(self.launcher) )

        # Configure and Add Autonomous Mode to SmartDashboard
        self.m_chooser = wpilib.SendableChooser()
        self.m_chooser.setDefaultOption("1 - None", commands2.cmd.none() )
        self.m_chooser.addOption("2 - Autonomous Command", autonomous.SampleAuto1() )
        wpilib.SmartDashboard.putData("Autonomous Mode", self.m_chooser)
        
        # Configure Driver 1 Button Mappings
        self.m_driver1 = commands2.button.CommandXboxController(0)
        # B button go brrrr
        self.m_driver1.b().whileTrue( commands.RunLauncher(self.launcher) )
        #change launcher speeds
        self.m_driver1.leftBumper().whileTrue(commands.DecrementLauncherSpeed(self.launcher))
        self.m_driver1.rightBumper().whileTrue(commands.IncrementLauncherSpeed(self.launcher))

        # Configure Driver 2 Button Mappings
        '''self.m_driver1 = commands2.button.CommandXboxController(0)
        self.m_driver1.a().whileTrue( sequences.SampleSequence() )'''

        # Configure Default Commands
        #self.subsystem.setDefaultCommand(
        #    commands.SampleCommand1()
        #)

    def getAutonomousCommand(self) -> commands2.Command:
        """
        :returns: the autonomous command that has been selected from the ShuffleBoard
        """
        return self.m_chooser.getSelected()
