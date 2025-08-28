#!/usr/bin/env python3

#  ******************************************************************************
#  * This program is protected under international and U.S. copyright laws as
#  * an unpublished work. This program is confidential and proprietary to the
#  * copyright owners. Reproduction or disclosure, in whole or in part, or the
#  * production of derivative works therefrom without the express permission of
#  * the copyright owners is prohibited.
#  *
#  *                Copyright (C) 2024 by Dolby Laboratories,
#  *                Copyright (C) 2024 by Dolby International AB.
#  *                            All rights reserved.
#  ******************************************************************************/
import zlib
import math
import sys
import xml.etree.ElementTree as ET


def ber_length_encode(length):
    # Reference: ISO/IEC 8824-1:2003, Section 8.1.3
    # Definite form
    if length < 128:
        output_bytes = bytearray(1)
        output_bytes[0] = length
        return output_bytes
    num_bytes_req = math.ceil(math.ceil(math.log2(length)) / 8.0)
    output_bytes = bytearray(num_bytes_req + 1)
    output_bytes[0] = 0x80 | num_bytes_req
    for i in range(0, num_bytes_req):
        output_bytes[i + 1] = length >> ((num_bytes_req - i - 1) * 8) & 0xff
    return output_bytes


def ber_length_decode(f):
    # get first byte
    byte_zero = int.from_bytes(f.read(1), 'big')
    if byte_zero < 128:
        return 1, byte_zero
    num_bytes = byte_zero & 0x7f
    length = 0
    for i in range(0, num_bytes):
        length = length + (int.from_bytes(f.read(1), 'big') << ((num_bytes - i - 1) * 8))
    return num_bytes + 1, length


class MGASection:
    identifier = -1
    length = 0
    value_position = 0

    def __init__(self):
        self.identifier = -1
        self.length = 0
        self.value_position = 0


class MGAInfo:
    channels = 0
    bits_per_sample = 0
    samplerate = 0
    file_size = 0
    timecode = ''

    def __init__(self):
        # set default values
        self.channels = 0
        self.bits_per_sample = 0
        self.samplerate = 0
        self.file_size = 0
        self.timecode = ''


class MGAFrame:
    num_sections = 0
    audio_section = MGASection()
    metadata_sections = []

    def __init__(self):
        self.num_sections = 0
        self.audio_section = MGASection()
        self.metadata_sections = []


class MGAFile:
    f = None
    numSamples = 0
    metadata_header_bytes = bytearray(0)
    metadata_payload_bytes = bytearray(0)
    no_compress = False
    debug = False
    mode = None
    info = None

    def __init__(self, filename, mode):
        if mode == 'w':
            self.f = open(filename, 'wb')
        elif mode == 'r':
            self.f = open(filename, 'rb')
            self.init_info_object()
        else:
            raise Exception('Invalid file access mode')
        self.noCompress = False
        self.debug = False
        self.mode = mode

    def close(self):
        self.f.close()

    def __del__(self):
        if self.f is not None:
            self.f.close()

    def debug_on(self):
        self.debug = True

    def compress_off(self):
        self.no_compress = True

    def print_debug(self):
        print('metadata header size: ', len(self.metadata_header_bytes))
        print('metadata payload size: ', len(self.metadata_payload_bytes))
# --------------------------------------------------------------------------------------------------------------
# Muxing
# --------------------------------------------------------------------------------------------------------------

    def add_sadm_xml(self, sadm_xml):
        if self.mode != 'w':
            raise Exception('Invalid Mode')

        if self.no_compress:
            version_format_bytes = b'\x00\x00' # version = 0, format = 0
            self.metadata_payload_bytes = version_format_bytes + bytes(sadm_xml, 'utf-8')
        else:
            version_format_bytes = b'\x00\x01' # version = 0, format = 1
            bytes_to_compress = bytes(''.join(sadm_xml), 'utf-8')
            gzip_compress = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
            self.metadata_payload_bytes = version_format_bytes + gzip_compress.compress(bytes_to_compress) + gzip_compress.flush()
            if self.debug:
                verify_bytes = zlib.decompress(self.metadata_payload_bytes, 15 + 32)
                if verify_bytes != bytes_to_compress:
                    print('Compression verification failed')
                    sys.exit(-1)
                else:
                    print('Compression verification passed')

        ber_length_bytes = ber_length_encode(len(self.metadata_payload_bytes))
        mga_frame_length: int = 1 + len(ber_length_bytes) + len(self.metadata_payload_bytes)

        self.metadata_header_bytes = bytearray(7 + len(ber_length_bytes))

        self.metadata_header_bytes[0] = 1 # Index=1, first metadata section
        self.metadata_header_bytes[1] = 0x2 # Identifier = 0x2, single payload beginning with Tag
        self.metadata_header_bytes[2] = mga_frame_length >> 24
        self.metadata_header_bytes[3] = (mga_frame_length >> 16) & 0xff
        self.metadata_header_bytes[4] = (mga_frame_length >> 8) & 0xff
        self.metadata_header_bytes[5] = mga_frame_length & 0xff
        self.metadata_header_bytes[6] = 0x12  # Serial ADM Payload tag
        self.metadata_header_bytes[7:7 + len(ber_length_bytes)] = ber_length_bytes

    def write_audio(self, audio_frame):

        # First write section count
        # S.M.P.T.E ST 2127-1:2022 Table 1 MGA Frame
        audio_length = len(audio_frame)
        audio_header_bytes = bytearray(7)
        audio_header_bytes[0] = 2   
        audio_header_bytes[1] = 0
        audio_header_bytes[2] = 0
        audio_header_bytes[3] = audio_length >> 24
        audio_header_bytes[4] = (audio_length >> 16) & 0xff
        audio_header_bytes[5] = (audio_length >> 8) & 0xff
        audio_header_bytes[6] = audio_length & 0xff


        self.f.write(audio_header_bytes)
        self.f.write(audio_frame)
        self.f.write(self.metadata_header_bytes)
        self.f.write(self.metadata_payload_bytes)

# --------------------------------------------------------------------------------------------------------------
# DeMuxing
# --------------------------------------------------------------------------------------------------------------
    def get_bytes_processed(self):
        return self.f.tell()

    def get_id_length_value(self):
        output_section = MGASection()
        index = int.from_bytes(self.f.read(1), "big")
        output_section.identifier = int.from_bytes(self.f.read(1), 'big')
        output_section.length = int.from_bytes(self.f.read(4), 'big')
        output_section.value_position = self.f.tell()
        # skip over value so we ready to ready next item
        self.f.seek(output_section.length, 1)
        return output_section

    def get_next_mga_frame(self):
        # Check for eof
        frame = MGAFrame()
        pos = self.f.tell()
        if pos == self.info.file_size:
            return None

        #SMPTE ST 2127-1 Table
        frame.num_sections = int.from_bytes(self.f.read(1), "big")
        if frame.num_sections != 2:            raise ValueError('Only 2 sections per MGA frame is supported')
        frame.audio_section = None
        frame.metadata_sections = []
        next_metadata_index = 1
        for section_no in range(0, frame.num_sections):
            index = int.from_bytes(self.f.read(1), "big")
            self.f.seek(-1, 1)  # rewind by one byte
            if index == 0:
                frame.audio_section = self.get_id_length_value()
                if frame.audio_section.identifier != 0:
                    raise ValueError("Expected identifier = 0 for Audio Essence")
            elif index == next_metadata_index and index != 0xff:
                frame.metadata_sections.append(self.get_id_length_value())
                if frame.metadata_sections[-1].identifier != 2:
                    raise ValueError("Only support single ST 2109 Payload")
                next_metadata_index = next_metadata_index + 1
            else:
                raise ValueError("Invalid Metadata Index")
        return frame

    def get_info(self):
        return self.info

    def init_info_object(self):
        # create object for return
        self.info = MGAInfo()
        self.f.seek(0, 2)  # seek to end
        self.info.file_size = self.f.tell()
        self.f.seek(0, 0)  # back to beginning

        # Check for empty file
        if self.info.file_size == 0:
            self.info = None
            return

        # get the first MGA frame
        mga_frame = self.get_next_mga_frame()
        # Return none is failed to get MGA frame
        if mga_frame is None:
            self.info = None
            return

        # get the first metadata section with S-ADM
        sadm_xml = str()
        for metadata_section in mga_frame.metadata_sections:
            sadm_xml = self.get_sadm(metadata_section)
            if sadm_xml == bytes():
                break
        # load up XML into Element Tree
        self.update_info_with_xml(sadm_xml)
        self.f.seek(0, 0) # rewind to start of file
        # Need to determine bits_per sample, channels, num_frames

    def eof(self):
        return self.f.tell() == self.info.file_size

    def get_time_code(self):
        return self.info.timecode

    def get_audio(self, audio_section: MGASection):
        # don't change file position so save it
        pos = self.f.tell()
        self.f.seek(audio_section.value_position, 0)
        audio = self.f.read(audio_section.length)
        # restore position
        self.f.seek(pos, 0)
        return audio

    def get_sadm(self, metadata_section: MGASection) -> bytes:
        # don't change file position so save it
        pos = self.f.tell()
        self.f.seek(metadata_section.value_position, 0)
        # Check tag matches S-ADM payload
        tag = int.from_bytes(self.f.read(1), 'big')
        if tag != 0x12:
            self.f.seek(pos, 0)
            print("Warning: Mismatched metadata tag!")
            return bytes()
        length_size, length = ber_length_decode(self.f)
        version = int.from_bytes(self.f.read(1), 'big')
        if version != 0:
            raise ValueError('ST2109 payload version number not 0')
        sadm_format = int.from_bytes(self.f.read(1), 'big')
        if sadm_format == 0:
            sadm_xml = self.f.read(length - 2) # length field includes version and format
        elif sadm_format == 1:
            gzip_data = self.f.read(length - 2) # length field includes version and format
            try:
                sadm_xml = zlib.decompress(gzip_data, 15 + 32)
            except zlib.error:
                raise Exception('Unzipping of gzipped payload failed')
        else:
            raise ValueError('Unknown S-ADM format (Table 2, ST 2127-10)')

        # return to starting position
        self.f.seek(pos, 0)
        return sadm_xml

    def update_info_with_xml(self, sadm_xml):
        try:
            tree = ET.ElementTree(ET.fromstring(sadm_xml))
        except ET.ParseError:
            raise Exception("Error: failed to parse input XML")

        root = tree.getroot()
        frame_header_root = root.find('frameHeader')
        frame_format = frame_header_root.find('frameFormat')
        adm_format_extended_root = root.find('audioFormatExtended')
        uid_elements = adm_format_extended_root.findall('audioTrackUID')
        bits_per_sample = 0
        samplerate = 0
        for i in range(0, len(uid_elements)):
            uid_bits_per_sample = uid_elements[i].get('bitDepth')
            uid_samplerate = uid_elements[i].get('sampleRate')
            if uid_bits_per_sample != None:
                if bits_per_sample == 0:
                    bits_per_sample = int(uid_bits_per_sample)
                else:
                    if bits_per_sample != int(uid_bits_per_sample):
                        raise Exception("Bit Depth in file is inconsistent")
            if uid_samplerate != None:
                if samplerate == 0:
                    samplerate = int(uid_samplerate)
                else:
                    if samplerate != int(uid_samplerate):
                        raise Exception("Sampling Rate in file is inconsistent")
        timecode = frame_format.get('start')
        if bits_per_sample > 0:
            self.info.bits_per_sample = bits_per_sample
        if samplerate > 0:
            self.info.samplerate = samplerate
        if len(timecode) > 0:
            self.info.timecode = timecode
        transport_track_format_root = frame_header_root.find('transportTrackFormat')
        audio_tracks = transport_track_format_root.findall('audioTrack')
        if len(audio_tracks) > 0:
            self.info.channels = len(audio_tracks)

    def read(self):
        mga_frame = self.get_next_mga_frame()
        audio = self.get_audio(mga_frame.audio_section)
        sadm_xmls = []
        for metadata_section in mga_frame.metadata_sections:
            sadm_xml = self.get_sadm(metadata_section)
            if len(sadm_xml) > 0:
                sadm_xmls.append(sadm_xml)
            else:
                print("Warning: Dropped null sadm payload")
        # update time code
        if len(sadm_xmls) > 0:
            self.update_info_with_xml(sadm_xmls[0])
        else:
            print("Warning: No valid sadm found in MGA frame")
        return audio, sadm_xmls


