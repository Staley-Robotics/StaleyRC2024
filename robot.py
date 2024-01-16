import wpilib
import hal
import commands2
import RobotContainer


class MyRobot(wpilib.TimedRobot):
    def robotInit(self):
        # Start Logging using the built in DataLogManager
        try:
            wpilib.DataLogManager.start( dir='/U/logs' )
        except:
            wpilib.DataLogManager.start()
        wpilib.DriverStation.startDataLog(wpilib.DataLogManager.getLog())

        self.m_robotContainer = RobotContainer.RobotContainer()
        #hal.report(
        #    hal.tResourceType.kResourceType_Framework,
        #    hal.tInstances.kFramework_RobotBuilder
        #)

    def robotPeriodic(self):
        wpilib.setCurrentThreadPriority(True, 99)
        commands2.CommandScheduler.getInstance().run()
        wpilib.setCurrentThreadPriority(True, 10)

    def autonomousInit(self):
        self.m_autonomousCommand:commands2.Command = self.m_robotContainer.getAutonomousCommand()

        if self.m_autonomousCommand != None:
            self.m_autonomousCommand.schedule()

    def autonomousPeriodic(self): pass
    def autonomousExit(self):
        if self.m_autonomousCommand != None:
            self.m_autonomousCommand.cancel()

    def teleopInit(self): pass
    def teleopPeriodic(self): pass
    def teleopExit(self): pass

    def testInit(self): pass
    def testPeriodic(self): pass
    def testExit(self): pass

    def disabledInit(self): pass
    def disabledPeriodic(self): pass
    def disabledExit(self): pass

    def _simulationInit(self): pass
    def _simulationPeriodic(self): pass
    def _simluationExit(self): pass
