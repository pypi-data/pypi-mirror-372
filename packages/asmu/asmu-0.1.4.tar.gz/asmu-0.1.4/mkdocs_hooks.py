import subprocess
import sys
from typing import Literal


def on_startup(command: Literal['build', 'gh-deploy', 'serve'],
               dirty: bool) -> None:
    print("mkdocs_hooks.py: Generating figures...")
    # generate pyreverse graphs
    subprocess.run(["pyreverse", "asmu", "--output", "svg", "--output-directory", "docs/imgs/"], check=True)
    # generate figures
    subprocess.run([sys.executable, "examples/plot_gainramp.py"], check=True)
    subprocess.run([sys.executable, "examples/plot_noise.py"], check=True)
    print("...DONE")
