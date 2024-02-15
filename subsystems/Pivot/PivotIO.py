import wpiutil.wpistruct

import dataclasses

class PivotIO:

    @wpiutil.wpistruct.make_wpistruct(name='PivotIOInputs')
    @dataclasses
    class PivotIOInputs:
        foo:float = 0.0
    
    def __init__(self) -> None:
        pass

    def updateInputs(self, inputs:PivotIOInputs) -> None:
        pass

    """copied from Tyler's LuancherIO, adapt to equivalent"""
    # def run(self) -> None:
    #     pass

    # def stop(self) -> None:
    #     pass

    # def setVelocity(self, leftVelocity:float, rightVelocity:float) -> None:
    #     pass

    # def getVelocity(self) -> [float, float]:
    #     return [0.0, 0.0]

    # def atSetpoint(self, errorRange:float = 0.0) -> [bool, bool]:
    #     leftVeloc, rightVeloc = self.getVelocity()
    #     leftSp, rightSp = self.getSetpoint()
    #     leftAtSpeed = abs( leftSp - leftVeloc ) < errorRange
    #     rightAtSpeed = abs( rightSp - rightVeloc ) < errorRange
    #     return [ leftAtSpeed, rightAtSpeed ]
    
    # def getSetpoint(self) -> [float, float]:
    #     return [0.0, 0.0]