import logging
import sys
from pathlib import Path
from typing import Sequence

import click

from converter.motionarea import MotionArea

log = logging.getLogger(__name__)
global_logger = logging.getLogger()
global_logger.setLevel(logging.DEBUG)

stdout_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s %(levelname)-8s %(message)s ", datefmt="%m-%d-%y %H:%M:%S"
)
stdout_handler.setFormatter(formatter)
global_logger.addHandler(stdout_handler)


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.option("--silent/--no-silent", default=False)
@click.pass_context
def homing_convert(ctx, debug: bool, silent: bool):
    """Auto conversion of motorhome 1.0 scripts to motorhome 2.0"""
    if debug:
        stdout_handler.setLevel(logging.DEBUG)
    elif silent:
        stdout_handler.setLevel(logging.WARNING)
    else:
        stdout_handler.setLevel(logging.INFO)


@homing_convert.command()
@click.argument("root", type=click.Path(file_okay=False, exists=True), default=".")
def motion(root: str):
    """
    Scan a DLS Motion Area for homing PLC generating scripts and convert them
    all to v2.0

    - Looks for Master.pmc files to determine the PLC Numbers.
    - Looks for files called generate_homing_plc.py and converts them to
      generate_homing_plc2.py
    - Generates a set of PLCs using generate_homing_plc2.py and verifies that they
      match the existing PLCs

    Args:
        root (str): The root folder of the Motion Area to be scanned
    """
    motion_path = Path(root)

    motionarea = MotionArea(motion_path)
    log.info(f"trying homing conversion for {motion_path} in {motionarea.root_path}")

    motionarea.make_old_motion()
    motionarea.make_new_motion()
    try:
        motionarea.check_matches()
    except AssertionError as e:
        click.echo(e.args[0])


@homing_convert.command()
@click.argument("root", type=click.Path(file_okay=False, exists=True), default=".")
@click.argument("plc_file", type=click.Path(dir_okay=False), nargs=-1)
@click.option(
    "--infile",
    type=click.Path(dir_okay=False, exists=True),
    default="configure/generate_homing_plcs.py",
)
@click.option(
    "--outfile", type=click.Path(dir_okay=False), default="generate_homing_plcs2.py"
)
def file(infile: Path, outfile: Path, plc_name: Sequence[str]):
    """
    Convert a single v1.0 homing PLC generator python file to v2.0

    Args:
        infile (str): the path to the file to be converted
        outfile(str): the path to the output file which will be created or
          overwritten
        names: 0 or more PLC filenames to generate. These should be paths
        relative to generate_homing_plcs2.py. If none are supplied then all
        PLCs are generated, they are given sequential PLC numbers from 11
        and a relative folder 'PLCs'
    """
    # in_path = Path(infile)
    # out_path = Path(outfile)
    # root_path = Path(root)

    # motion_area = MotionArea(root_path)
    log.error("This feature is not yet implemented")
