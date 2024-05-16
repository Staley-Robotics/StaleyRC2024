import typing

from commands2 import SelectCommand
import commands2.cmd

from commands import PivotHandoff, PivotAim, PivotAmp, PivotSpeaker, PivotToss, PivotByStick
from subsystems import Pivot

class PivotDefault(SelectCommand):
    def __init__( self,
                  pivot:Pivot,
                  hasNote:typing.Callable[[],bool],
                  getAngle:typing.Callable[[],float],
                  getAdjustAxis:typing.Callable[[],float] = lambda: 0.0,
                  isTargetAmp:typing.Callable[[],bool] = lambda: False,
                  isIntakeQueued:typing.Callable[[],bool] = lambda: False,
                  useAutoCalculate:typing.Callable[[],bool] = lambda: True,
                  useManualAdjust:typing.Callable[[],bool] = lambda: False
                ):
        self.indexerHasNote = hasNote
        self.launchAngle = getAngle
        self.getAdjustAxis = getAdjustAxis
        self.isTargetAmp = isTargetAmp
        self.isIntakeQueued = isIntakeQueued
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
                # if self.launchAngle() < 15.5:
                #     return "toss"
                if self.isTargetAmp():
                    return "amp"
                else:
                    return "aim"
            else:
                return "handoff"
        elif self.useManualAdjust():
            if self.indexerHasNote():
                return "adjust"
            elif self.isIntakeQueued():
                return "handoff"
            else:
                return "wait"
        else:
            if self.indexerHasNote():
                if self.isTargetAmp():
                    return "amp"
                else:
                    return "fixed"
            elif self.isIntakeQueued():
                return "handoff"
            else:
                return "wait"

    def initialize(self):
        super().initialize()
        self.setName( self._selectedCommand.getName() )
        