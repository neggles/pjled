#!/usr/bin/env python3

from typing import List
import json
import click
import logging
import logzero

from pijuice import PiJuice

# Instantiate PiJuice interface object
pijuice = PiJuice(1, 0x14)
pj_led = "D2"

# do config for logging
logfmt = logzero.LogFormatter(datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__package__)


def hex2rgb(hexval) -> List:
    hexval = hexval.lstrip("#")
    lv = len(hexval)
    if lv == 6:
        ret = list(int(hexval[i : i + 2], 16) for i in (0, 2, 4))
    elif lv == 3:
        ret = list(int(hexval[i] + hexval[i], 16) for i in (0, 1, 2))
    logging.debug(f"hex2rgb: in={hexval} out={ret}")
    return ret


@click.group()
@click.version_option(package_name="pjled")
@click.option("-v", "--verbose", count=True, help="be more verbose")
def cli(verbose):
    # clamp log level to DEBUG
    loglevel = max(logging.WARNING - (verbose * 10), 10)
    logging.root = logzero.setup_logger(level=loglevel, isRootLogger=True, formatter=logfmt)
    logger.debug(
        f"verbose = {verbose}, loglevel: {logging.getLevelName(logger.getEffectiveLevel())}"
    )
    pass


@cli.command()
@click.option("-l", "--led", type=click.Choice(["D1", "D2"], case_sensitive=False), default=pj_led)
def clear(led):
    logging.info(f"turning off {led}")
    res1 = pijuice.status.SetLedBlink(led, 0, [0, 0, 0], 0, [0, 0, 0], 0)
    res2 = pijuice.status.SetLedState(led, [0, 0, 0])
    logging.info(f"result: blink={json.dumps(res1)} set={json.dumps(res2)}")
    pass


@cli.command()
@click.option("-l", "--led", type=click.Choice(["D1", "D2"], case_sensitive=False), default=pj_led)
@click.option("-c", "--color", default="3300aa", help="hex color to set (6cf, 66ccff)")
def set(led, color):
    logging.info(f"setting {led} to {color}")
    result = pijuice.status.SetLedState(led, hex2rgb(color))
    logging.info(f"result: {json.dumps(result)}")
    pass


@cli.command()
@click.option("-l", "--led", type=click.Choice(["D1", "D2"], case_sensitive=False), default=pj_led)
@click.option("-c", "--color", default="aa00aa", help="hex color to set (6cf, 66ccff)")
@click.option("-d", "--duration", default=250, help="on-duration")
def blink(led, color, duration):
    # clamp to 490ms on, 10ms off, and vice-versus
    ontime = max(10, min(duration, 490))
    # having sanitized ontime we can cheat here
    offtime = 500 - ontime

    logging.info(f"setting {led} to blink {color}, on={ontime}ms off={offtime}ms")
    result = pijuice.status.SetLedBlink(led, 255, hex2rgb(color), ontime, [0, 0, 0], offtime)
    logging.info(f"result: {json.dumps(result)}")
    pass


if __name__ == "__main__":
    cli()
