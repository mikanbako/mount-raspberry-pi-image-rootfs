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

# mount_raspberry_pi_image_rootfs
#
# A script that mount the root filesystem in an image of Raspberry Pi.

import argparse
import os.path
import subprocess
import sys

import fdisk_output_parser


class CannotDetectOffsetError(Exception):
    pass


def detect_root_filesystem_offset(fdisk_output):
    u'''
    Detect offset bytes of the root filesystem from an output of fdisk.

    Offset bytes is calculated by multiplying bytes of unit by start unit
    index of the root filesytem.

    Arguments:
        fdisk_output : An output of fdisk.
    Return:
        Offset bytes of the root filesystem.
    '''
    # Get partitions.

    try:
        image_partitions = fdisk_output_parser.detect_partitions(fdisk_output)
    except fdisk_output_parser.ParseError:
        raise CannotDetectOffsetError()

    # Get the offset of the root file system.

    for partition in image_partitions:
        if partition.system == u'Linux':
            return partition.start_offset_bytes
    else:
        raise CannotDetectOffsetError()


def detatch_loopback_device(loopback_device_file):
    subprocess.call(['losetup', '-d', loopback_device_file])


def main(image_file, loopback_device_file, mount_point):
    # Check the files exist.
    # If one of the file does not exist, print an error message and exit.

    if not os.path.exists(image_file):
        print >>sys.stderr, "Image file does not exist : " + image_file
        sys.exit(1)
    if not os.path.exists(loopback_device_file):
        print >>sys.stderr, \
            "Loopback device file does not exist : " + loopback_device_file
        sys.exit(1)
    if not os.path.exists(mount_point):
        print >>sys.stderr, "Mount point does not exist : " + mount_point
        sys.exit(1)

    # Set loopback device for the image.

    print '--- Set loopback device %s for %s ---' % (
        loopback_device_file, image_file)

    try:
        subprocess.check_call(
            ['losetup', loopback_device_file, image_file],
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        print >>sys.stderr, e
        sys.exit(1)

    # Get the offset of partition of the root filesystem.

    print '--- Get the offset of partition of the root filesystem ---'

    try:
        fdisk_output = subprocess.check_output(
            ['fdisk', '-lu', loopback_device_file],
            stderr=subprocess.STDOUT)
        offset = detect_root_filesystem_offset(fdisk_output)
    except subprocess.CalledProcessError, e:
        print >>sys.stderr, e
        detatch_loopback_device(loopback_device_file)
        sys.exit(1)
    except CannotDetectOffsetError:
        print >>sys.stderr, \
            "The offset of the root filesystem cannot be detected."
        detatch_loopback_device(loopback_device_file)
        sys.exit(1)

    # Mount the partition of the root filesystem.

    print '--- Mount the partition of the root filesystem ---'

    try:
        subprocess.check_call(
            ['mount', '-o', 'loop,offset=%d' % offset, loopback_device_file,
                mount_point],
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        print >>sys.stderr, e
        detatch_loopback_device(loopback_device_file)
        sys.exit(1)

    # Complete.

    print 'Success.'


def create_command_line_parser():
    parser = argparse.ArgumentParser(
        description=u'Mount the root filesystem in an image of Raspberry Pi.')

    parser.add_argument(
        'image_file', metavar='IMAGE_FILE', nargs='?')
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

    if arguments.image_file and arguments.loopback_device_file and \
            arguments.mount_point:
        main(arguments.image_file, arguments.loopback_device_file,
             arguments.mount_point)
    else:
        parser.print_help()
        sys.exit(1)
