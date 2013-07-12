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

# This script tests fdisk_output_parser.py.

import unittest

import fdisk_output_parser
import test_data


class TestCalculatedPartitionValues(unittest.TestCase):
    u'''
    Test whether calculated values of a Partition are valid.
    '''
    def setUp(self):
        self.__target = fdisk_output_parser.Partition(512, 1, 3, "dummy")

    def testStartOffsetBytes(self):
        self.assertEqual(1 * 512, self.__target.start_offset_bytes)

    def testEndOffsetBytes(self):
        self.assertEquals(3 * 512, self.__target.end_offset_bytes)


class TestDetectingPartitions(unittest.TestCase):
    def testDetectingPartition(self):
        u'''
        Test whether the partitions are detected.
        '''
        with open(test_data.FDISK_OUTPUT_FILE) as f:
            partitions = fdisk_output_parser.detect_partitions(f.read())

        self.assertEqual(2, len(partitions))
        self.assertPartition(
            512, 8192, 122879, u'W95 FAT32 (LBA)', partitions[0])
        self.assertPartition(512, 122880, 3788799, u'Linux', partitions[1])

    def assertPartition(
            self, bytes_par_unit, start_unit_index, end_unit_index, system,
            partition):
        self.assertEqual(bytes_par_unit, partition.bytes_par_unit)
        self.assertEqual(start_unit_index, partition.start_unit_index)
        self.assertEqual(end_unit_index, partition.end_unit_index)
        self.assertEqual(system, partition.system)

    def testInvalidFdiskOutput(self):
        u'''
        Test whether an exception is raised when the output of
        fdisk is invalid.
        '''
        with self.assertRaises(fdisk_output_parser.ParseError):
            fdisk_output_parser.detect_partitions(u'')
