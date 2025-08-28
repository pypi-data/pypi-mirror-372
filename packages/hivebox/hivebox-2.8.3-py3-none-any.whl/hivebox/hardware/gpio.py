import sys
from pathlib import Path
import re
from hivebox.common.cli import cli_print, cli_run, PrintColors

class GPIOSetup:
    @staticmethod
    def install_orangepi5b(library_path: Path):
        wiringOP_path = library_path / "wiringOP"
        cli_print("Starting GPIO installation...")
        cli_print("Cloning repository...")
        cli_run(f"git clone --recursive https://github.com/orangepi-xunlong/wiringOP-Python -b next {wiringOP_path}", label="Downloading WiringOp...")
        print(cli_run("pwd", workdir=wiringOP_path, stdout=True).stdout)
        cli_run(f"git submodule update --init --remote", workdir=wiringOP_path)
        result = cli_run(f"{sys.executable} generate-bindings.py", workdir=wiringOP_path, stdout=True)
        with wiringOP_path.joinpath('bindings.i').open('w') as f:
            f.write(result.stdout)
        cli_run(f"{sys.executable} setup.py install", workdir=wiringOP_path)
        cli_print("Installation complete")
        print(cli_run("gpio readall", workdir=wiringOP_path, stdout=True).stdout)
        import wiringpi  # NOQA
