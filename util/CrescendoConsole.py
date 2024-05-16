from commands2.button import CommandJoystick, Trigger

class CrescendoConsole:
    def __init__(self, port:int):
        self.joystick = CommandJoystick(port)

    def getX(self) -> float: return self.joystick.getRawAxis(0)
    def getY(self) -> float: return self.joystick.getRawAxis(1)

    def buttonLeftGreen(self) -> Trigger: return self.joystick.button(12)
    def buttonLeftBlue(self) -> Trigger: return self.joystick.button(11)
    def buttonLeftRed(self) -> Trigger: return self.joystick.button(10)
    def buttonMiddleWhite(self) -> Trigger: return self.joystick.button(4)
    def buttonRightGreen(self) -> Trigger: return self.joystick.button(1)
    def buttonRightBlue(self) -> Trigger: return self.joystick.button(2)
    def buttonRightYellow(self) -> Trigger: return self.joystick.button(3)

    def buttonToggleLeft(self) -> Trigger: return self.joystick.button(9)
    def buttonToggleMiddleTop(self) -> Trigger: return self.joystick.button(7)
    def buttonToggleMiddleBottom(self) -> Trigger: return self.joystick.button(8)
    def buttonToggleRightTop(self) -> Trigger: return self.joystick.button(6)
    def buttonToggleRightBottom(self) -> Trigger: return self.joystick.button(5)

    def toggleLeft(self) -> bool: return self.joystick.getHID().getRawButton(9)
    def toggleMiddleTop(self) -> bool: return self.joystick.getHID().getRawButton(7)
    def toggleMiddleBottom(self) -> bool: return self.joystick.getHID().getRawButton(8)
    def toggleRightTop(self) -> bool: return self.joystick.getHID().getRawButton(6)
    def toggleRightBottom(self) -> bool: return self.joystick.getHID().getRawButton(5)
