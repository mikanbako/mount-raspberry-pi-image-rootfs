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

# mount_image_partitions
#
# A script that mount or unmount partitions in a disk image.

import argparse
import collections
import os.path
import subprocess
import sys

import fdisk_output_parser


class OperationFailedError(Exception):
    def __init__(self, cause):
        self.__cause = cause

    @property
    def cause(self):
        return self.__cause


def detach_loopback_device(loopback_device_file):
    subprocess.call(['losetup', '-d', loopback_device_file])


def attach_partitions(
        partitions, loop_device_file_prefix, loop_device_start_number,
        image_file):
    u'''
    Attach partitions in an image file to loop devices.

    Arguments:
        partitions : A list of attaching Partitions.
        loop_device_file_prefix : A prefix of loop device file.
        loop_device_start_number : Start number of loop device.
        image_file : An image file that contains the partitions.
    Return:
        A dictionary that maps loop device to attached partition.
    Raise:
        OperationFailedError : When attaching partitions are failed.
    '''
    loop_device_number = loop_device_start_number
    attached_partition_map = collections.OrderedDict()
    try:
        # Attach partitions.
        for attaching_partition in partitions:
            loop_device_file = loop_device_file_prefix + \
                str(loop_device_number)

            subprocess.check_output([
                'losetup', '-o', str(attaching_partition.start_offset_bytes),
                '--sizelimit', str(attaching_partition.end_offset_bytes),
                loop_device_file, image_file], stderr=subprocess.STDOUT)

            attached_partition_map[loop_device_file] = attaching_partition
            loop_device_number += 1
    except subprocess.CalledProcessError, e:
        try:
            # Detach attached partitions.
            for loop_device_file in attached_partition_map.iterkeys():
                detach_loopback_device(loop_device_file)
        except subprocess.CalledProcessError, cleanUpError:
            raise OperationFailedError(cleanUpError)

        raise OperationFailedError(e)

    return attached_partition_map


def print_attaching_result(loop_device_partition_map):
    u'''
    Print the result of attaching result.

    Argument:
        loop_device_partition_map : A dictionary that maps loop device file to
                                    Partition.
    '''
    print 'number, loop device, system of partition'

    number = 0
    for loop_device_file, partition in loop_device_partition_map.iteritems():
        print '%d, %s, %s' % (number, loop_device_file, partition.system)
        number += 1


def detach_partitions(
        partitions_count, loop_device_file_prefix, loop_device_start_number):
    u'''
    Detach partitions.

    Arguments:
        partitions_count : A count of attached partitions.
        loop_device_file_prefix : A prefix of loop device file.
        loop_device_start_number : Start number of loop device.
    Return:
        A list of detached loop device files.
    Raise:
        OperationFailedError : When detaching partitions are failed.
    '''
    detached_loop_device_files = []
    try:
        for loop_device_number in range(
                loop_device_start_number,
                loop_device_start_number + partitions_count):
            loop_device_file = loop_device_file_prefix + \
                str(loop_device_number)

            subprocess.check_output(
                ['losetup', '-d', loop_device_file], stderr=subprocess.STDOUT)
            detached_loop_device_files.append(loop_device_file)
    except subprocess.CalledProcessError, e:
        raise OperationFailedError(e)

    return detached_loop_device_files


def print_detaching_result(detached_loop_device_files):
    u'''
    Print the result of detaching loop device files.

    Argument:
        detached_loop_device_files : A list of detached loop device files.
    '''
    print u'Detached loop device :'
    for loop_device_file in detached_loop_device_files:
        print loop_device_file


def detect_partitons(image_file):
    u'''
    Detect partitions in the image file.

    Argument:
        image_file : An image file.
    Return:
        A list of Partition in the image file.
    Raise:
        OperationFailedError : When detection partitions are failed.
    '''
    try:
        # Find a free loop device because the loop device with the start
        # number is used when detach is requested.
        loop_device_file_for_detecting = subprocess.check_output(
            ['losetup', '-f'], stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError, e:
        raise OperationFailedError(e)

    try:
        # Attach the image file.
        subprocess.check_output(
            ['losetup', loop_device_file_for_detecting, image_file],
            stderr=subprocess.STDOUT)

        # Get fdisk output.
        fdisk_output = subprocess.check_output(
            ['fdisk', '-lu', loop_device_file_for_detecting],
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        detach_loopback_device(loop_device_file_for_detecting)
        raise OperationFailedError(e)

    try:
        # Detach from the loop device for detecting partitions.
        detach_loopback_device(loop_device_file_for_detecting)
    except subprocess.CalledProcessError, e:
        raise OperationFailedError(e)

    try:
        return fdisk_output_parser.detect_partitions(fdisk_output)
    except fdisk_output_parser.ParseError, e:
        raise OperationFailedError(e)


def main(loop_device_file_prefix, loop_device_start_number, is_attach,
         image_file):
    # Check the image file is available.
    # If it is not available, exit with help message.

    if not os.path.exists(image_file):
        print >>sys.stderr, u'Image file is not found : ' + image_file
        sys.exit(1)

    # Detect partitions in the image file.

    partitions = detect_partitons(image_file)

    # If attach is requested, attach partitions.
    # If detach is requested, detach partitions.
    # And print result.

    if is_attach:
        result = attach_partitions(
            partitions, loop_device_file_prefix, loop_device_start_number,
            image_file)
        print_attaching_result(result)
    else:
        result = detach_partitions(
            len(partitions), loop_device_file_prefix, loop_device_start_number)
        print_detaching_result(result)


def create_command_line_parser():
    parser = argparse.ArgumentParser(
        description=
        u'Attach or detach partitions in a disk image to loop devices.')
    parser.add_argument(
        '-l', '--loopdevice', dest='loop_device_files_prefix',
        default=u'/dev/loop', help=u'Prefix of loop device files.')
    parser.add_argument(
        '-s', '--start_number', dest='loop_device_start_number',
        type=int, default=0, help=u'Start number of loop device files.')
    parser.add_argument(
        '-d', '--detach', dest='is_attach', action='store_false',
        default=True, help=u'Detach partitions.')
    parser.add_argument(
        'image_file', metavar='IMAGE_FILE', nargs='?',
        help="Path of an image file.")

    return parser


if __name__ == '__main__':
    # Parse command line arguments.

    parser = create_command_line_parser()
    arguments = parser.parse_args()

    # Call main function if image file is available.
    # If image file is not available, exit with help message.

    if arguments.image_file:
        try:
            main(
                arguments.loop_device_files_prefix,
                arguments.loop_device_start_number,
                arguments.is_attach,
                arguments.image_file)
        except OperationFailedError, e:
            causeException = e.cause
            if isinstance(causeException, subprocess.CalledProcessError):
                print >>sys.stderr, causeException.output + str(causeException)
            else:
                print >>sys.stderr, causeException
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
