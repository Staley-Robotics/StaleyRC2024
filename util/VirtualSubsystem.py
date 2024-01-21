VirtualSubsystemInst = None

class VirtualSubsystem:
    systems = []

    def __init__(self) -> None:
        self.systems.append( self )

    def periodicForAll(self) -> None:
        pass

    def periodic(self) -> None:
        pass

if __name__ == "__main__":
    VirtaulSubsystemInst = VirtualSubsystem()