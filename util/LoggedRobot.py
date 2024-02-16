import sys
import typing

import hal
from wpilib import IterativeRobotBase

from .Logger import Logger

class AutoLogOutputManager:
    def __init__(self):
        pass

    def registerFields(self, cls):
        pass

class DriverStationJNI:
    def observeUserProgramStarting(self):
        pass

class NotifierJNI:
    def __init__(self):
        pass

    @staticmethod
    def initializeNotifier() -> int:
        return 1

    def setNotifierName(self, notifier:int, name:str) -> None:
        pass

    def stopNotifier(self, notifier:int) -> None:
        pass

    def cleanNotifier(self, notifier:int) -> None:
        pass

    def updateNotifierAlarm(self, notifier:int, nextCycle:int):
        pass

    def waitForNotifierAlarm(self, notifier:int):
        pass

class LoggedRobot(IterativeRobotBase):
    defaultPeriod:float = 0.02
    notifier:int = NotifierJNI.initializeNotifier()
    periodUs:int = 0
    nextCycleUs:int = 0

    useTiming:bool = True

    @typing.overload
    def __init__(self):
        self.__init__(self, self.defaultPeriod)

    def __init__(self, period):
        super().__init__( period )
        self.periodUs = int( period * 1000000)
        NotifierJNI.setNotifierName(self.notifier, "LoggedRobot")

        hal.report(
            hal.tResourceType.kResourceType_Framework,
            hal.tInstances.kFramework_AdvantageKit
        )

    def finalize(self) -> None:
        NotifierJNI.stopNotifier(self.notifier)
        NotifierJNI.cleanNotifier(self.notifier)
        pass

    def startCompetition(self) -> None:
        # Robot init methods
        initStart = Logger.getRealTimestamp()
        self.robotInit()
        if self.isSimulation():
            self._simulationInit()
        initEnd = Logger.getRealTimestamp()
            
        # Register auto logged outputs
        AutoLogOutputManager.registerFields(self)
            
        # Save Data from Init Cycle
        Logger.periodicAfterUser(initEnd - initStart, 0)
            
        # Tell the DS taht the robot is ready to be enabled
        sys.stdout.write("********** Robot program startup complete **********")
        DriverStationJNI.observeUserProgramStarting()
            
        # Loop forever, calling the appropriate mode-dependent function
        while True:
            if self.useTiming:
                currentTimeUs = Logger.getRealTimestamp()

                if self.nextCycleUs < currentTimeUs:
                    self.nextCycleUs = currentTimeUs
                else:
                    NotifierJNI.updateNotifierAlarm( self.notifier, self.nextCycleUs )
                    NotifierJNI.waitForNotifierAlarm( self.notifier)

                self.nextCycleUs += self.periodUs
            
            periodicBeforeStart = Logger.getRealTimestamp()
            Logger.periodicBeforeUser()
            userCodeStart = Logger.getRealTimestamp()
            self._loopFunc()
            userCodeEnd = Logger.getRealTimestamp()
            Logger.periodicAfterUser(userCodeEnd - userCodeStart, userCodeStart - periodicBeforeStart)


    def endCompetition(self) -> None:
        NotifierJNI.stopNotifier( self.notifier )

    def setUseTiming( self, useTiming:bool ):
        self.useTiming = useTiming