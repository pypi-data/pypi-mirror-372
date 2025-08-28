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

import argparse
import sys
import os
import subprocess
import math
import xml.etree.ElementTree as Et
import uuid
import soundfile as sf
from soundfile import SEEK_END
import time
import mga.mga_file


__version__ = 'v0.9.6'


def get_cmd_stdio(args):
    run_output = subprocess.run(args, stdout=subprocess.PIPE)
    text = str(run_output.stdout.decode("utf-8"))
    text = text.replace('\\n', '\n')
    text = text.replace('\\r', '\r')
    text = text.replace('\\t', '\t')
    return text


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

#        0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |   identifier  |                     length                    |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |               | S-ADM PL Tag  |      length (BER encoded)     |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   :                             ....                              |
#   +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
#   |   version     |     format    |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


frame_sizes = [(24, [2000]), (25, [1920]),
               (29.97, [1602, 1601, 1602, 1601, 1602]),
               (30, [1600]), (50, [960]),
               (59.94, [801, 801, 801, 801, 800]),
               (60, [800])]


def update_frame_format_id(frame_format_element, frame_count):
    frame_format_element.set('frameFormatID', str('FF_' + ("{0:0{1}x}".format(frame_count, 8))))


# converts a contiguous set of 32 bytes samples to 24 bit
# endian is little as per ST382
def ndarray_to_24bits_bytes(arr):
    output = bytearray(b'')
    for x in arr:
        for y in x:
            y_int = int(y) >> 8
            y_bytes = y_int.to_bytes(3, "little", signed=True)
            output += bytearray(y_bytes)
    return output


def main():
    parser = argparse.ArgumentParser(description='Metadata Guided Audio (MGA) Muxer')

    parser.add_argument('-is', '--input_sadm_xml', type=argparse.FileType('r'),
                        default="input_sadm.xml", help='Serial ADM XML filename for input (default: %(default)s)')
    parser.add_argument('-ia', '--input_audio_wav', type=argparse.FileType('r'),
                        default="input_audio.wav", help='Audio wav filename for input (default: %(default)s)')
    parser.add_argument('-om', '--output_mga', type=argparse.FileType('w'),
                        default="mga_muxer_out.mga", help='Output MGA file (default: %(default)s)')
    parser.add_argument('-os', '--output_xml', type=argparse.FileType('w'),
                        default="mag_muxer_out.xml", help='1st modified S-ADM XML frame (default: %(default)s)')
    parser.add_argument('-f', '--frame_rate', type=float,
                        default=25,
                        help='mga frame rate in frames per second: 24,25,29.97,30,50,59.94 or 60 (default: %(default)s)')
    parser.add_argument('--compress', action='store_const', const=True,
                        default=False, help='Applies gzip compression to XML before muxing (default: %(default)s)')
    parser.add_argument('--debug', action='store_const',  const=True,
                        default=False, help='Enables debug mode (default: %(default)s)')
    args = parser.parse_args()

    frame_rate_cadence = []
    for frame_rate_tuple in frame_sizes:
        if args.frame_rate == frame_rate_tuple[0]:
            frame_rate_cadence = frame_rate_tuple[1]
    if len(frame_rate_cadence) == 0:
        raise "Error: invalid frame rate must be either 24, 25, 29.97, 50, 59.94 or 60"

    if args.input_sadm_xml is not None:
        sadm_xml_file = open(args.input_sadm_xml.name, "r")
        # Read entire contents into string
        sadm_xml_str = sadm_xml_file.read()
        sadm_xml_file.close()
    else:
        raise "Error: no input filename"

    audio_wav_file = None
    if args.input_audio_wav is not None:
        try:
            audio_wav_file = sf.SoundFile(args.input_audio_wav.name)
        except sf.SoundFileError as e:
            raise sf.SoundFileError("Error: Bad Wave file input",e , e.args)
    else:
        print("Error: no input filename")
        exit(-4)

    if not audio_wav_file.seekable():
        raise ValueError("Wavfile not compatible with seeking")

    # Element tree from XML string, find S-ADM frame frameFormat sub-element and all audioFormatExtended UID elements
    try:
        tree = Et.ElementTree(Et.fromstring(sadm_xml_str))
    except Et.ParseError as e:
        raise Et.ParseError("Error: failed to parse input XML", e, e.args)

    root = tree.getroot()
    frame_header_root = root.find('frameHeader')
    frame_format = frame_header_root.find('frameFormat')
    adm_format_extended_root = root.find('audioFormatExtended')
    uid_elements = adm_format_extended_root.findall('audioTrackUID')

    # Update S-ADM element frameFormat attribute flowID with new UUID
    frame_format.set('flowID', str(uuid.uuid4()))

    num_audio_samples = audio_wav_file.seek(0, SEEK_END)

    if audio_wav_file.subtype == 'PCM_16':
        bits_per_sample = "16"
    else:
        bits_per_sample = "24"

    # Insert and set all UID element occurrences with attributes sampleRate and bitDepth from info in wave file
    for i in range(0, len(uid_elements)):
        uid_elements[i].set('sampleRate', str(audio_wav_file.samplerate))
        uid_elements[i].set('bitDepth', str(bits_per_sample))

    xml_decl = '<?xml version="1.0" encoding="UTF-8"?>' + '\n'

    # Ensure that frame format has the right number of digits
    update_frame_format_id(frame_format, 1)

    # Write out the modified XML file
    if args.output_xml is not None:
        with open(args.output_xml.name, 'w') as f:
            tree_str = Et.tostring(root, encoding='utf-8', ).decode()
            f.write(xml_decl + tree_str)

    filename = args.output_mga.name
    mga_file_h = mga.mga_file.MGAFile(filename, 'w')

    if not args.compress:
        mga_file_h.compress_off()
    if args.debug:
        mga_file_h.debug_on()

    cadence_counter = 0
    samples_left = num_audio_samples
    seek_position = 0
    new_position = 0
    frame_no = 1
    print("Creating ", filename, "...")
    start_time = time.time()
    frame_size_samples = frame_rate_cadence[cadence_counter]

    while (samples_left >= frame_size_samples) and (new_position == seek_position):
        # Update S-ADM frame counter and update (compress) metadata payload for this frame
        update_frame_format_id(frame_format, frame_no)
        frame_format.set('duration', f'00:00:00.0{frame_size_samples:0>4}S48000')
        tree_str = Et.tostring(root, encoding='utf-8',).decode()
        mga_file_h.add_sadm_xml(xml_decl + tree_str)
        cadence_counter = (cadence_counter + 1) % len(frame_rate_cadence)
        new_position = audio_wav_file.seek(seek_position)

        if bits_per_sample == "16":
            audio_frame = audio_wav_file.read(frame_size_samples, dtype="int16")
            mga_file_h.write_audio(audio_frame.tobytes())
        else:
            audio_frame = audio_wav_file.read(frame_size_samples, dtype="int32")
            mga_file_h.write_audio(ndarray_to_24bits_bytes(audio_frame))

        # update counters
        seek_position += frame_size_samples
        new_position = audio_wav_file.seek(seek_position)
        samples_left -= frame_size_samples
        frame_no = frame_no + 1
        frame_size_samples = frame_rate_cadence[cadence_counter]

        # print progress
        percent_complete = ((num_audio_samples - samples_left) / num_audio_samples) * 100
        time_elapsed = time.time() - start_time
        time_remaining = ((100 - percent_complete) / percent_complete) * time_elapsed
        time_remaining_str = time.strftime("%H:%M:%S", time.gmtime(time_remaining))
        sys.stdout.write("\rCompleted " + str(int(percent_complete)) + "%,  Time Remaining " + time_remaining_str)

    if args.debug:
        mga_file_h.print_debug()
    mga_file_h.close()
    print("\nMGA File successfully created")
    root = Et.Element("root")

    Et.SubElement(root, "channels").text = str(audio_wav_file.channels)
    Et.SubElement(root, "bitDepth").text = str(bits_per_sample)
    Et.SubElement(root, "samplingRate").text = str(audio_wav_file.samplerate)

    tree = Et.ElementTree(root)
    filename_stem, filename_ext = os.path.splitext(filename)
    tree.write(filename_stem + ".audio_info.xml")



if __name__ == '__main__':
    main()
