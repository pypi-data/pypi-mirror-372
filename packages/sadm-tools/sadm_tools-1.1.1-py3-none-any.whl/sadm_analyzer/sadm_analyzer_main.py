#!/usr/bin/env python3

# ******************************************************************************
# * This program is protected under international and U.S. copyright laws as
# * an unpublished work. This program is confidential and proprietary to the
# * copyright owners. Reproduction or disclosure, in whole or in part, or the
# * production of derivative works therefrom without the express permission of
# * the copyright owners is prohibited.
# *
# *                Copyright (C) 2023 by Dolby Laboratories,
# *                Copyright (C) 2023 by Dolby International AB.
# *                            All rights reserved.
# ******************************************************************************/

import os
import sys
import subprocess
import zlib
import math
import argparse
import wave
import struct

# Constants
MAX_START_SYNC_SEARCH = 48000
MAX_BURST_SPACING = 4096
PA_LE = [0x6f8720, 0x96f872]
PB_LE = [0x54e1f0, 0xa54e1f]
BD_20 = 0
BD_24 = 1
VERSION = 'v1.0.1'


class ReadWavFile:
    f = None

    def __init__(self, filename):
        self.f = wave.open(filename, "rb")

    def read_data(self, number_of_samples):
        return self.f.readframes(number_of_samples)

    def get_file_info(self):
        return self.f.getparams()

    def close(self):
        self.f.close()


class State:
    IDLE = 0
    GOT_PA1 = 1
    GOT_PA2 = 2
    GOT_SYNC = 3
    GOT_HEADER = 4
    GOT_GZIP_FRAME = 5


def main():
    st2116_bits = None
    first_pa = None
    second_pa = None
    assemble_info = None
    format_info = None

    parser = argparse.ArgumentParser(description='sADM Analyzer')
    parser.add_argument('-i', '--input_file', required=True, type=argparse.FileType('r'), default=None, help='File to analyze')
    args = parser.parse_args()

    f = ReadWavFile(args.input_file.name)
    file_info = f.get_file_info()
    p = '<' + str(file_info.nchannels * file_info.sampwidth) + 'B'
    print('sadm_analyzer ' + VERSION)

    # Hunt for Pa
    state = State.IDLE
    for i in range(0, MAX_START_SYNC_SEARCH):
        data = struct.unpack(p, f.read_data(1))
        a = data[0]
        b = data[1]
        c = data[2]
        d = a
        d = d | b << 8
        d = d | c << 16

        if state == State.IDLE:
            if d == PA_LE[BD_20]:
                st2116_bits = 20
                state = State.GOT_PA1
                first_pa = i

            if d == PA_LE[BD_24]:
                st2116_bits = 24
                state = State.GOT_PA1
                first_pa = i

        if state == State.GOT_PA1:
            if st2116_bits == 20:
                if d == PB_LE[BD_20]:
                    state = State.GOT_SYNC
            if st2116_bits == 24:
                if d == PB_LE[BD_24]:
                    state = State.GOT_SYNC

        if state == State.GOT_PA1:
            print('Found' + ' ' + str(st2116_bits) + 'bit mode' + ' ' + 'Pa' + ' ' + 'at sample' + ' ' + str(i))
        elif state == State.GOT_SYNC:
            print('Found' + ' ' + str(st2116_bits) + 'bit mode' + ' ' + 'Sync' + ' ' + 'at sample' + ' ' + str(i))
            break

    if not state == State.GOT_SYNC:
        print('Failed to find sync')
        f.close()
        return

    pc = struct.unpack(p, f.read_data(1))
    pd = struct.unpack(p, f.read_data(1))
    pe = struct.unpack(p, f.read_data(1))
    pf = struct.unpack(p, f.read_data(1))

    # f.close()

    # Decode Pc
    a = pc[0]
    b = pc[1]
    c = pc[2]
    d = a
    d = d | b << 8
    d = d | c << 16

    data_type = (d & 0x001f00) >> 8
    data_mode = (d & 0x006000) >> 13
    error_flag = (d & 0x008000) >> 15
    changed_metadata_flag = (d & 0x010000) >> 16
    assemble_flag = (d & 0x020000) >> 17
    format_flag = (d & 0x040000) >> 18
    multiple_chunk_flag = (d & 0x180000) >> 19
    data_stream_number = (d & 0xe00000) >> 21

    print('*** ST2116 Summary ***')
    print('Burst Info (Pc)' + ' ' + hex(d))
    print('  data_type:' + str(data_type))
    print('  data_mode:' + str(data_mode))
    print('  error_flag:' + str(error_flag))

    print('  changed_metadata_flag:' + str(changed_metadata_flag))
    print('  assemble_flag:' + str(assemble_flag))
    print('  format_flag:' + str(format_flag))

    print('  multiple_chunk_flag:' + str(multiple_chunk_flag))
    print('  data_stream_number:' + str(data_stream_number))

    # Decode Pd
    a = pd[0]
    b = pd[1]
    c = pd[2]
    d = a
    d = d | b << 8
    d = d | c << 16
    print('Burst length (Pd)' + ' ' + hex(d))

    # Decode Pe
    a = pe[0]
    b = pe[1]
    c = pe[2]
    d = a
    d = d | b << 8
    d = d | c << 16
    print('Extended data type (Pe)' + ' ' + hex(d))

    # Decode Pf
    a = pf[0]
    b = pf[1]
    c = pf[2]
    d = a
    d = d | b << 8
    d = d | c << 16
    print('Reserved (Pf)' + ' ' + hex(d))

    # If assemble_info of format_info then display those words
    if assemble_flag == 1:
        assemble_info = struct.unpack(p, f.read_data(1))
        if format_flag == 1:
            format_info = struct.unpack(p, f.read_data(1))
    else:
        if format_flag == 1:
            format_info = struct.unpack(p, f.read_data(1))

    if assemble_flag == 1:
        a = assemble_info[0]
        b = assemble_info[1]
        c = assemble_info[2]
        d = a
        d = d | b << 8
        d = d | c << 16
        print('Assemble Info' + ' ' + hex(d))

    if format_flag == 1:
        a = format_info[0]
        b = format_info[1]
        c = format_info[2]
        d = a
        d = d | b << 8
        d = d | c << 16
        print('Format Info' + ' ' + hex(d))

    f.close()

    # Find sample spacing between frames
    state = State.IDLE
    f = ReadWavFile(args.input_file.name)
    file_info = f.get_file_info()
    p = '<' + str(file_info.nchannels * file_info.sampwidth) + 'B'

    # Hunt for first and second Pa, find distance between
    for i in range(0, MAX_START_SYNC_SEARCH):
        data = struct.unpack(p, f.read_data(1))
        a = data[0]
        b = data[1]
        c = data[2]
        d = a
        d = d | b << 8
        d = d | c << 16

        if state == State.GOT_PA1:
            if d == PA_LE[BD_20]:
                st2116_bits = 20
                state = State.GOT_PA2
                second_pa = i

            if d == PA_LE[BD_24]:
                st2116_bits = 24
                state = State.GOT_PA2
                second_pa = i

        if state == State.IDLE:
            if d == PA_LE[BD_20]:
                st2116_bits = 20
                state = State.GOT_PA1
                first_pa = i

            if d == PA_LE[BD_24]:
                st2116_bits = 24
                state = State.GOT_PA1
                first_pa = i

    f.close()
    if state == State.GOT_PA2:
        print()
        print('Frame spacing is' + ' ' + str(second_pa - first_pa) + ' ' + 'samples,' + ' ' + 'framerate =' + ' ' + str(48000/(second_pa - first_pa)) + 'fps')

    return

if __name__ == '__main__':
    print("Starting...")
    main()
