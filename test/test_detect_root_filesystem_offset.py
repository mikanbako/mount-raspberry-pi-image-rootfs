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

# This script tests detecting the root filesystem from an output of fdisk.

import os.path
import unittest

import mount_raspberry_pi_image_rootfs


class TestDetectRootFilesystem(unittest.TestCase):
    def testValidOutput(self):
        u'''
        Test that offset byte is (unit byte) * (offset unit) when
        the output of fdisk is valid.
        '''
        FDISK_OUTPUT_FILE = os.path.join(
            os.path.dirname(__file__), u'fdisk_output.txt')

        with open(FDISK_OUTPUT_FILE) as f:
            offset = mount_raspberry_pi_image_rootfs.\
                detect_root_filesystem_offset(f.read())

        self.assertEqual(512 * 122880, offset)

    def testInvalidOutput(self):
        u'''
        Test that CannotDetectOffsetError raises when the output of fdisk is
        invalid.
        '''
        with self.assertRaises(
                mount_raspberry_pi_image_rootfs.CannotDetectOffsetError):
            mount_raspberry_pi_image_rootfs.detect_root_filesystem_offset("")