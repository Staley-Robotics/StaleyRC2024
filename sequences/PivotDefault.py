import commands2

from commands import *
from subsystems import Pivot
from util import *

class PivotDefault(commands2.SelectCommand):
    def __init__( self,
                  pivot:Pivot,
                  hasNote:typing.Callable[[],bool],
                  getAngle:typing.Callable[[],float],
                  getAdjustAxis:typing.Callable[[],float] = lambda: 0.0,
                  isTargetAmp:typing.Callable[[],bool] = lambda: False,
                  isIntakeWaiting:typing.Callable[[],bool] = lambda: False,
                  useAutoCalculate:typing.Callable[[],bool] = lambda: True,
                  useManualAdjust:typing.Callable[[],bool] = lambda: False
                ):
        self.indexerHasNote = hasNote
        self.launchAngle = getAngle
        self.getAdjustAxis = getAdjustAxis
        self.isTargetAmp = isTargetAmp
        self.isIntakeWaiting = isIntakeWaiting
        self.useAutoCalculate = useAutoCalculate
        self.useManualAdjust = useManualAdjust

        super().__init__(
            {
                "handoff": PivotHandoff(pivot),
                "aim": PivotAim(pivot, getAngle),
                "amp": PivotAmp(pivot),
                "fixed": PivotSpeaker(pivot),
                "toss": PivotToss(pivot),
                "adjust": PivotByStick(pivot, getAdjustAxis),
                "wait": commands2.cmd.none().withName("PivotWait")
            },
            self.getState
        )

    def getState(self):
        if self.useAutoCalculate():
            if self.indexerHasNote():
                if self.launchAngle() < 10.0:
                    return "toss"
                elif self.isTargetAmp():
                    return "amp"
                else:
                    return "aim"
            else:
                return "handoff"
        elif self.useManualAdjust():
            if self.indexerHasNote():
                return "adjust"
            elif self.isIntakeWaiting():
                return "handoff"
            else:
                return "wait"
        else:
            if self.indexerHasNote():
                return "fixed"
            elif self.isIntakeWaiting():
                return "handoff"
            else:
                return "wait"

    def initialize(self):
        super().initialize()
        self.setName( self._selectedCommand.getName() )
        