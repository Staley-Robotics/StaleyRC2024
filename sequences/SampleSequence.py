import commands2

import commands

class SampleSequence(commands2.SequentialCommandGroup):
    def __init__(self):
        super().__init__()

        self.addCommands( commands.SampleCommand1() )
        self.addCommands( commands.SampleCommand2() )