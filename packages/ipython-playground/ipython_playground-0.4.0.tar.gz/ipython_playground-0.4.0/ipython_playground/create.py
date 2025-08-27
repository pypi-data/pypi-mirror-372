import os

from ipython_playground.utils import log


def create_playground_file():
    log.info("Creating playground.py file")
    with open("playground.py", "w") as f:
        f.write("""#!/usr/bin/env -S uv run ipython -i
# isort: off
import ipython_playground

globals().update(ipython_playground.all_extras())
                
ipython_playground.output()
""")
    log.info("Setting executable permissions on playground.py")
    os.chmod("playground.py", 0o755)
