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


# Constants
Pa_16 = 0xf872
Pb_16 = 0x4e1f

Pa_20 = 0x6f872
Pb_20 = 0x54e1f
Pc_20 = 0x053f0
H2_20 = 0x00010
H2_20_nozip = 0x00000

Pa_24 = 0x96f872
Pb_24 = 0xa54e1f
Pc_24 = 0x055f00
H2_24 = 0x000100
H2_24_nozip = 0x000000

Pe = 0x00001
Pf = 0x00000

__version__ = 'v2.3.1'


def get_cmd_stdio(args):
    run_output = subprocess.run(args, stdout=subprocess.PIPE)
    text = str(run_output.stdout.decode("utf-8"))
    text = text.replace('\\n', '\n')
    text = text.replace('\\r', '\r')
    text = text.replace('\\t', '\t')
    return text


def file_remove(filenames):
    for file in filenames:

        try:
            os.remove(file)
        except:
            pass


def subframe_to_bytes(b, bit_depth=20, endian='little'):
    if bit_depth == 20:
        if endian == 'big':
            l = b & 0x000ff
            m = (b & 0x0ff00) >> 8
            h = (b & 0xf0000) >> 16
            b = (l << 12) | (m << 4) | h
        bo = (b * 16).to_bytes(3, byteorder='little')
        # Now output zeros for right channel
        bo = bo + (0).to_bytes(3, byteorder='little')
    elif bit_depth == 24:
        bo = b.to_bytes(3, byteorder='little')
        # Now output zeros for right channel
        bo = bo + (0).to_bytes(3, byteorder='little')
    else:
        raise(ValueError("Invalid bit depth"))
    return bo


def bytes_to_samples(bytesList, bit_depth=20, endian='little'):
    if bit_depth == 20:
        numOutputBytes = int((math.ceil(len(bytesList) * 8) / 20.0) * 6)
        nibbleIn = False
        nibble = 0  # for safety
        outputBytes = b''
        # round up to make all input bytes are processed
        numNibbles = len(bytesList) * 2
        numExtraNibbles = numNibbles % 5

        if numExtraNibbles > 0:
            extraBytesNeeded = math.ceil((5 - numExtraNibbles) / 2.0)
            # add zeros to the end as needed to get full 20 bits
            for i in range(0, extraBytesNeeded):
                bytesList.append(0)
        byteIndex = 0
        while len(outputBytes) < numOutputBytes:
            # Get next 20 bits
            if nibbleIn is True:
                b = nibble << 16
                b = b | bytesList[byteIndex] << 8
                byteIndex = byteIndex + 1
                b = b | bytesList[byteIndex]
                byteIndex = byteIndex + 1
                nibbleIn = False
            else:
                b = bytesList[byteIndex] << 12
                byteIndex = byteIndex + 1
                b = b | bytesList[byteIndex] << 4
                byteIndex = byteIndex + 1
                b = b | bytesList[byteIndex] >> 4
                nibble = bytesList[byteIndex] & 0xf
                nibbleIn = True
                byteIndex = byteIndex + 1
            outputBytes = outputBytes + subframe_to_bytes(b, bit_depth, endian)
    elif bit_depth == 24:
        numOutputBytes = int((math.ceil(len(bytesList) * 8) / 24.0) * 6)
        outputBytes = b''
        # round up to make all input bytes are processed
        numNibbles = len(bytesList) * 2
        numExtraNibbles = numNibbles % 6

        if numExtraNibbles > 0:
            extraBytesNeeded = math.ceil((6 - numExtraNibbles) / 2.0)
            # add zeros to the end as needed to get full 20 bits
            for i in range(0, extraBytesNeeded):
                bytesList.append(0)
        byteIndex = 0
        while len(outputBytes) < numOutputBytes:
            b = bytesList[byteIndex] << 16
            byteIndex = byteIndex + 1
            b = b | bytesList[byteIndex] << 8
            byteIndex = byteIndex + 1
            b = b | bytesList[byteIndex]
            byteIndex = byteIndex + 1
            outputBytes = outputBytes + subframe_to_bytes(b, bit_depth, endian)
    else:
        raise(ValueError("Invalid Bit Depth"))

    return outputBytes


def clean_up_text(lines):
    for index in range(0,len(lines)):
        lines[index] = lines[index].rstrip()
        lines[index] = lines[index].rstrip('\n')
        if len(lines[index]) > 0:
            lines[index] = lines[index] + '\n'
        else:
            lines.remove(lines[index])


class ADMWavFile:
    f = None
    numSamples = 0
    headerBytes = []

    def __init__(self, filename):
        self.f = wave.open(filename, "wb")
        self.f.setnchannels(2)
        self.f.setsampwidth(3)
        self.f.setframerate(48000)
        self.numSamples = 0
        self.headerBytes = b''

    def close(self):
        self.f.close()

    def __del__(self):
        if self.f is not None:
            self.f.close()

    def getNumSamples(self):
        return self.numSamples

    def add_subframe_to_header(self, b, bit_depth=20, endian='little'):
        self.headerBytes = self.headerBytes + subframe_to_bytes(b, bit_depth, endian)

    def output_guardband(self):
        self.f.writeframes(self.headerBytes)
        self.numSamples = self.numSamples + (int(len(self.headerBytes) / 6))

    def output_header(self):
        self.f.writeframes(self.headerBytes)
        self.numSamples = self.numSamples + (int(len(self.headerBytes) / 6))

    def output_raw_samples(self, rawBytes):
        self.f.writeframes(rawBytes)
        self.numSamples = self.numSamples + (int(len(rawBytes) / 6))

    def output_20bits_subframe(self, b, endian='little'):
        if endian == 'big':
            l = b & 0x000ff
            m = (b & 0x0ff00) >> 8
            h = (b & 0xf0000) >> 16
            b = (l << 12) | (m << 4) | h
        bo = (b * 16).to_bytes(3, byteorder='little')
        self.f.writeframes(bo)
        # Now output zeros for right channel
        bo = (0).to_bytes(3, byteorder='little')
        self.f.writeframes(bo)
        self.numSamples = self.numSamples + 1

    def output_24bits_subframe(self, b, endian='little'):
        if endian == 'big':
            l = b & 0x000ff
            m = (b & 0x0ff00) >> 8
            h = (b & 0xf0000) >> 16
            b = (l << 16) | (m << 8) | h
        bo = b.to_bytes(3, byteorder='little')
        self.f.writeframes(bo)
        # Now output zeros for right channel
        bo = (0).to_bytes(3, byteorder='little')
        self.f.writeframes(bo)
        self.numSamples = self.numSamples + 1

    def output_bytes_subframe(self, bytesList, bit_depth=20, endian='little'):
        samples = bytes_to_samples(bytesList, bit_depth, endian)
        self.output_raw_samples()

    def output_padding(self, numSamples):
        # declare padding multiplying by number of bytes in sample and
        padding = bytearray(numSamples * 3 * 2)
        self.f.writeframes(padding)


def main():
    frameSizeDict = {23.98: [2002], 24: [2000], 25: [1920], 29.97: [1602, 1601, 1602, 1601, 1602], 30: [1600],
                     50: [960], 59.94: [801, 801, 800, 801, 801], 60: [800],
                     100: [480], 119.88: [400, 401, 400, 401, 400], 120: [400]}

    parser = argparse.ArgumentParser(description='Serial ADM stream authoring applications')
    parser.add_argument('-i', '--input_sadm_xml', required=True, type=argparse.FileType('r'),
                        default=None, help='Serial ADM XML filename for input')
    parser.add_argument('-o', '--output_wav', required=True, type=argparse.FileType('w'),
                        default=None, help='output WAV filename containing serial ADM stream')
    parser.add_argument('-f', '--frame_rate', type=float,
                        default="25", help='Output video frame rate (23.98/24/25/29.97/30/50/59.94/60/100/119.88/120')
    parser.add_argument('-t', '--time', type=float,
                        default="10.0", help='Output frame length in seconds (rounded up to next video frame)')
    parser.add_argument('-g', '--gzip', type=argparse.FileType('w'),
                        default=None, help='output gzip payload file')
    parser.add_argument('-n', '--nozip', type=bool,
                        default=False, help='Do not use gzip for compression')
    parser.add_argument('-b', '--bit_depth', type=int,
                        default=24, choices=[20, 24], help='ST2116 bit depth')
    parser.add_argument('-debug', action='store_const', default=False, const=True, help='Enables debug mode')
    args = parser.parse_args()

    if args.frame_rate not in frameSizeDict:
        print("Error: bad frame rate!")
        parser.print_help()
        sys.exit(1)

    frameSizes = frameSizeDict[args.frame_rate]

    if (args.input_sadm_xml is not None):
        sadmXmlFile = open(args.input_sadm_xml.name, "r")
        sadmXML = sadmXmlFile.readlines()
        sadmXmlFile.close()

    bytesToCompress = bytes(''.join(sadmXML), 'utf-8')
    gzip_compress = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
    gzipData = gzip_compress.compress(bytesToCompress) + gzip_compress.flush()

    print('sadm2wav version ' + __version__)

    if args.debug:
        verifyBytes = zlib.decompress(gzipData, 15 + 32)
        if verifyBytes != bytesToCompress:
            print("Compression verification failed")
            sys.exit(-1)
        else:
            print("Compression verification passed")

    if args.gzip is not None:
        with open(args.gzip.name, "wb") as f:
            f.write(gzipData)
        if args.debug:
            print("Created gzip file:", args.gzip.name)

    # Get length of zipfile
    if args.nozip:
        if args.debug:
            print("Selected plain XML packing (not Gzipped)")
        sadmPayloadBytes = len(bytesToCompress);
    else:
        if args.debug:
            print("Selected Gzipped packing")
        sadmPayloadBytes = len(gzipData)
    if args.debug:
        print("sadmPayloadBytes: ", sadmPayloadBytes)

    sadmPayloadBits = sadmPayloadBytes * 8
    if args.debug:
        print("sadmPayloadBits: ", sadmPayloadBits)

    if args.bit_depth == 20:
        # Round up to an entire 20 bit sample
        sadmPayloadBits = math.ceil(sadmPayloadBits / 20.0) * 20
        if args.debug:
            print("Rounded Up sadmPayloadBits", sadmPayloadBits)
        zipSizeSamples = int(sadmPayloadBits / 20)
    elif args.bit_depth == 24:
        # Round up to an entire 24 bit sample
        sadmPayloadBits = math.ceil(sadmPayloadBits / 24.0) * 24
        if args.debug:
            print("Rounded Up sadmPayloadBits", sadmPayloadBits)
        zipSizeSamples = int(sadmPayloadBits / 24)
    else:
        raise ValueError("Invalid bit depth")

    if args.debug:
        print("zipSizeSamples", zipSizeSamples)

    if zipSizeSamples > min(frameSizes):
        print("Input xml is too big to fit in video frame")
        print("Use a lower frame rate or reduce size of XML")
        os.remove(args.output_wav.name)
        sys.exit(-2)

    numFrames = math.ceil(args.time * args.frame_rate)

    wavFile = ADMWavFile(args.output_wav.name)
    frameSizeIndex = 0

    wavFile.add_subframe_to_header(0, args.bit_depth)
    wavFile.add_subframe_to_header(0, args.bit_depth)
    wavFile.add_subframe_to_header(0, args.bit_depth)
    wavFile.add_subframe_to_header(0, args.bit_depth)

    if args.bit_depth == 20:
        wavFile.add_subframe_to_header(Pa_20, args.bit_depth)
        wavFile.add_subframe_to_header(Pb_20, args.bit_depth)
        wavFile.add_subframe_to_header(Pc_20, args.bit_depth)
    elif args.bit_depth == 24:
        wavFile.add_subframe_to_header(Pa_24, args.bit_depth)
        wavFile.add_subframe_to_header(Pb_24, args.bit_depth)
        wavFile.add_subframe_to_header(Pc_24, args.bit_depth)

    wavFile.add_subframe_to_header(sadmPayloadBits + 80, args.bit_depth)
    wavFile.add_subframe_to_header(Pe, args.bit_depth)
    wavFile.add_subframe_to_header(Pf, args.bit_depth)

    # Set the format flag in the format info word depending on whether the
    # XML is zipped or not
    if args.bit_depth == 20:
        if args.nozip:
            wavFile.add_subframe_to_header(H2_20_nozip, args.bit_depth)
        else:
            wavFile.add_subframe_to_header(H2_20, args.bit_depth)
    if args.bit_depth == 24:
        if args.nozip:
            wavFile.add_subframe_to_header(H2_24_nozip, args.bit_depth)
        else:
            wavFile.add_subframe_to_header(H2_24, args.bit_depth)

    if args.nozip:
        payload_bytes = bytes_to_samples(bytearray(bytesToCompress), args.bit_depth, 'little')
    else:        
        payload_bytes = bytes_to_samples(bytearray(gzipData), args.bit_depth, 'little')

    for frameNo in range(0, numFrames):
        wavFile.output_header()
        wavFile.output_raw_samples(payload_bytes)
        wavFile.output_padding(frameSizes[frameSizeIndex] - 11 - zipSizeSamples)
        frameSizeIndex = frameSizeIndex + 1
        if frameSizeIndex == len(frameSizes):
            frameSizeIndex = 0

    print("Wave file successfully Created")
    wavFile.close()


if __name__ == '__main__':
    main()