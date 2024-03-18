import commands2

from commands import *
from sequences.NoteToss import NoteToss
from sequences.NoteLaunchSpeaker import NoteLaunchSpeaker
from sequences.NoteLoadGround import NoteLoadGround
from subsystems import Intake, Indexer, Pivot, Elevator, Launcher
from util import *

class NoteAction(commands2.ConditionalCommand):
    def __init__(self, intake:Intake, indexer:Indexer, launcher:Launcher, pivot:Pivot, elevator:Elevator, getPose:typing.Callable[[],Pose2d]):
        super().__init__(
            # commands2.ConditionalCommand(
            #     NoteLaunchSpeaker(indexer, launcher, pivot, elevator, getPose),
            #     NoteToss(indexer, launcher, pivot, elevator),
            #     lambda: getPose().Y() > 6.00 
            # ),
            NoteLaunchSpeaker(indexer, launcher, pivot, elevator, getPose),
            NoteLoadGround(intake, indexer, pivot, elevator),
            indexer.hasNote
        )

    def initialize(self):
        super().initialize()
        self.setName( self.selectedCommand.getName() )
        