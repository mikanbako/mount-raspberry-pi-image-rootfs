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

# fdisk_output_parser
#
# A module that parses an output of fdisk.

import re


class ParseError(Exception):
    pass

# Patterns for parsing.

UNIT_PATTERN = re.compile(ur'^Units.+?(?P<bytes>\d+)\s+bytes$')

PARTITION_LIST_HEADER_PATTERN = re.compile(
    ur'^\s+Device\s+Boot\s+Start\s+.+$')

PARTITION_LIST_ITEM_PATTERN = re.compile(
    ur'^(?P<device>\S+)\s+?\*?\s+' +
    ur'(?P<start_unit_index>\d+)\s+' +
    ur'(?P<end_unit_index>\d+)\s+' +
    ur'\d+\s+' +
    ur'\S+\s+' +
    ur'(?P<system>.+)$')


class Partition:
    def __init__(
            self, bytes_par_unit, start_unit_index, end_unit_index, system):
        self.__bytes_par_unit = bytes_par_unit
        self.__start_unit_index = start_unit_index
        self.__end_unit_index = end_unit_index
        self.__system = system

    @property
    def bytes_par_unit(self):
        return self.__bytes_par_unit

    @property
    def start_unit_index(self):
        return self.__start_unit_index

    @property
    def start_offset_bytes(self):
        return self.start_unit_index * self.bytes_par_unit

    @property
    def end_unit_index(self):
        return self.__end_unit_index

    @property
    def end_offset_bytes(self):
        return self.end_unit_index * self.bytes_par_unit

    @property
    def system(self):
        return self.__system


def detect_partitions(fdisk_output):
    u'''
    Parse an output of fdisk and detect partitions.

    Parameters:
        fdisk_output : An output string of fdisk.
    Return:
        A list that contains Partitions. If there is not partition,
        an empty list is returned.
    Raise:
        ParseError : When the output of fdisk is invalid.
    '''

    # Detection is composed of the below phases.
    UNIT_DETECTION_PHASE = 0
    PARTITION_LIST_HEADER_DETECTION_PHASE = 1
    PARTITION_LIST_ITEM_DETECTION_PHASE = 2

    # Parse the output of fdisk.
    # This process assumes that the version of fdisk is util-linux 2.20.1.

    partitions = []
    current_phase = UNIT_DETECTION_PHASE
    for line in fdisk_output.splitlines():
        if current_phase == UNIT_DETECTION_PHASE:
            match = UNIT_PATTERN.match(line)
            if match:
                bytes_par_unit = int(match.group(u'bytes'))
                current_phase = PARTITION_LIST_HEADER_DETECTION_PHASE
        elif current_phase == PARTITION_LIST_HEADER_DETECTION_PHASE:
            match = PARTITION_LIST_HEADER_PATTERN.match(line)
            if match:
                current_phase = PARTITION_LIST_ITEM_DETECTION_PHASE
        elif current_phase == PARTITION_LIST_ITEM_DETECTION_PHASE:
            match = PARTITION_LIST_ITEM_PATTERN.match(line)
            if match:
                start_unit_index = int(match.group(u'start_unit_index'))
                end_unit_index = int(match.group(u'end_unit_index'))
                system = unicode(match.group(u'system'))

                partitions.append(
                    Partition(
                        bytes_par_unit, start_unit_index,
                        end_unit_index, system))

    # Check the detection is complete.

    if current_phase != PARTITION_LIST_ITEM_DETECTION_PHASE:
        raise ParseError()

    return partitions
