#!/usr/bin/env python3
# file: bmp280-monitor.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2018-04-22T20:56:36+0200
# Last modified: 2018-04-25T19:06:15+0200
"""
Monitoring program for the Bosch BMP280 temperature and pressure sensor.
The sensor is connected to the computer via an FT232H using I²C.

"""

from datetime import datetime
import argparse
import sys
import time

from pyftdi.spi import SpiController
from BMP280 import BMP280SPI


__version__ = '1.0'


def main(argv):
    """
    Entry point for bmp280-monitor.py

    Arguments:
        argv: command line arguments
    """

    now = datetime.utcnow().strftime('%FT%TZ')
    args = process_arguments(argv)

    # Connect to the sensor.
    ctrl = SpiController()
    ctrl.configure('ftdi://ftdi:232h/1')
    spi = ctrl.get_port(0)
    spi.set_frequency(100000)
    bmp280 = BMP280SPI(spi)

    # Open the data file.
    datafile = open(args.path.format(now), 'w')

    # Write datafile header.
    datafile.write('# BMP280 data.\n# Started monitoring at {}.\n'.format(now))
    datafile.write('# Per line, the data items are:\n')
    datafile.write('# * UTC date and time in ISO8601 format\n')
    datafile.write('# * Temperature in °C\n')
    datafile.write('# * Pressure in Pa\n')
    datafile.flush()

    # Read and write the data.
    try:
        while True:
            now = datetime.utcnow().strftime('%FT%TZ')
            temperature, pressure = bmp280.read()
            line = '{} {:.2f} {:.0f}\n'.format(now, temperature, pressure)
            datafile.write(line)
            datafile.flush()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        sys.exit(1)


def process_arguments(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-i',
        '--interval',
        default=5,
        type=int,
        help='interval between measurements (≥5 s, default 5 s)')
    parser.add_argument(
        '-v', '--version', action='version', version=__version__)
    parser.add_argument(
        'path',
        nargs=1,
        help=r'path template for the data file. Should contain {}. '
             r'For example "/tmp/bmp280-{}.d"')
    args = parser.parse_args(argv)
    args.path = args.path[0]
    if not args.path or r'{}' not in args.path:
        parser.print_help()
        sys.exit(0)
    if args.interval < 5:
        args.interval = 5
    return args


if __name__ == '__main__':
    main(sys.argv[1:])
