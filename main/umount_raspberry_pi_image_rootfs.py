#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2013 Keita Kita
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# umount_raspberry_pi_image_rootfs
#
# A script that unmount the root filesystem in an image of Raspberry Pi.

import argparse
import subprocess
import sys


def main(loopback_device_file, mount_point):
    # This function does not check any error. Because this function forces to
    # unmount and detach.

    # Unmount the mount point.

    subprocess.call(['umount', mount_point], stderr=subprocess.STDOUT)

    # Detach the loop device.

    subprocess.call(
        ['losetup', '-d', loopback_device_file], stderr=subprocess.STDOUT)


def create_command_line_parser():
    parser = argparse.ArgumentParser(
        description=
        u'Unmount the root filesystem in an image of Raspberry Pi.')

    parser.add_argument(
        'loopback_device_file', metavar='LOOPBACK_DEVICE_FILE', nargs='?')
    parser.add_argument(
        'mount_point', metavar='MOUNT_POINT', nargs='?')

    return parser


if __name__ == '__main__':
    # Parse command-line arguments.

    parser = create_command_line_parser()
    arguments = parser.parse_args()

    # Call main function with parsed arguments.
    # If there is not arguments, print help and exit.

    if arguments.loopback_device_file and arguments.mount_point:
        main(arguments.loopback_device_file, arguments.mount_point)
    else:
        parser.print_help()
        sys.exit(1)
