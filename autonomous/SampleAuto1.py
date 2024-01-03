import commands2

import commands
import sequences

class SampleAuto1(commands2.SequentialCommandGroup):
    def __init__(self):
        super().__init__()

        self.addCommands( commands.SampleCommand1() )
        self.addCommands( sequences.SampleSequence() )
