import typing

class VirtualSubsystem:
    def __init__(self) -> None:
        VirtualSubsystemInstance.append( self )

    def periodic(self) -> None:
        pass

class VirtualSubsystemInst:
    systems:typing.List[VirtualSubsystem] = []

    def append(self, system:VirtualSubsystem):
        self.systems.append(system)

    def periodic(self) -> None:
        for i in range(len( self.systems )):
            self.systems[i].periodic()

VirtualSubsystemInstance:VirtualSubsystemInst = None
if __name__ == "__main__":
    VirtaulSubsystemInst = VirtualSubsystemInst()