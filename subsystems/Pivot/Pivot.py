import wpilib

import wpiutil.wpistruct
import dataclasses

from commands2 import Subsystem

from wpilib import *

from phoenix5 import *
from phoenix5.sensors import CANCoder

from util import *

from util import *

class Pivot(Subsystem):
    class PivotPositions:
        #using degrees
        __priv__ = {
            0: NTTunableFloat( "/Config/PivotPositions/Bottom", -20 ),
            1: NTTunableFloat( "/Config/PivotPositions/Top", 55 ),
            2: NTTunableFloat( "/Config/PivotPositions/Amp", -20 ),
            3: NTTunableFloat( "/Config/PivotPositions/Trap", -20 ),
            4: NTTunableFloat( "/Config/PivotPositions/Source", 50 ),
        }

        Bottom = __priv__[0].get()
        Top = __priv__[1].get()
        Amp = __priv__[2].get()
        Trap = __priv__[3].get()
        Source = __priv__[4].get()

    def __init__(self, pivot:PivotIO):
        self.pivot = pivot
        self.pivotInputs = pivot.PivotIOInputs
        self.pivotLogger = NetworkTableInstance.getDefault().getStructTopic( "/Pivot", PivotIO.PivotIOInputs ).publish()

        self.offline = NTTunableBoolean( "/OfflineOverride/Pivot", False )


    def periodic(self):
        #logging
        self.pivot.update_inputs(self.pivotInputs)
        self.pivotLogger.set(self.pivotInputs)

        # Run Subsystem
        if RobotState.isDisabled() or self.offline.get():
            self.stop()
        
        self.pivot.run()
    
    def set_pos(self):
        pass
