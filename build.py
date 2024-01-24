import os
from pathlib import Path

def scandir( dir, recursionText="" ) -> str:
    text = """"""
    
    for e1 in os.scandir( dir ):
        print(e1.path)
        if e1.is_dir():
            text += scandir( e1, f"{recursionText}.{e1.name}")
        elif e1.name.endswith(".py") and e1.name != "__init__.py":
            f = e1.name.removesuffix(".py")
            text += f"from {recursionText}.{f} import *\n"
        else:
            pass
     
    return text

for p in [ 'autonomous', 'commands', 'sequences', 'subsystems', 'util' ]:
    dir = Path( p )
    text = scandir( dir )
    (dir / '__init__.py').write_text( text )
