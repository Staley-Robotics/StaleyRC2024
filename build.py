import os
from pathlib import Path

for p in [ 'autonomous', 'commands', 'sequences', 'subsystems', 'util' ]:
    dir = Path( p )

    text = """"""
    for file in os.listdir( dir ):
        
        if file.endswith(".py") and file != "__init__.py":
            f = file.removesuffix(".py")
            text += f"from .{f} import *\n"

        (dir / '__init__.py').write_text(
            text
        )