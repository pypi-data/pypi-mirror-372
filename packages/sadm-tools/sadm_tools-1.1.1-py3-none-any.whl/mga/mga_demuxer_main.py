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
import soundfile as sf
import time
import mga.mga_file
import numpy as np
import math
import xml.etree.ElementTree as Et

__version__ = 'v0.9.4'


def get_cmd_stdio(args):
    run_output = subprocess.run(args, stdout=subprocess.PIPE)
    text = str(run_output.stdout.decode("utf-8"))
    text = text.replace('\\n', '\n')
    text = text.replace('\\r', '\r')
    text = text.replace('\\t', '\t')
    return text


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


def sadm_frame_compare(sadm_frame1, sadm_frame2):
    lines1 = sadm_frame1.splitlines()
    lines2 = sadm_frame2.splitlines()
    if len(lines1) != len(lines2):
        return True


def convert_bytes_to_24bit_np_array(ab, channels):
    num_frames = math.floor(len(ab) / (3 * channels))
    if num_frames == 0:
        return None
    output_array = np.empty([num_frames, channels], dtype='int32')
    bc = 0
    with np.nditer(output_array, op_flags=['readwrite']) as it:
        for sample in it:
            # Little Endian as per ST382
            sample[...] = int.from_bytes(ab[bc:bc+3], byteorder='little', signed=True) << 8
            bc = bc + 3
    return output_array


def main():
    parser = argparse.ArgumentParser(description='Metadata Guided Audio (MGA) Demuxer')
    parser.add_argument('-im', '--input_mga_file', type=argparse.FileType('r'),
                        default='input_mga.mga', help='MGA filename for input (default: %(default)s)')
    parser.add_argument('-oa', '--output_audio_wav', type=argparse.FileType('w'),
                        default='mga_demux_out.wav', help='Audio wav filename for output (default: %(default)s)')
    parser.add_argument('-os', '--output_sadm_xml_folder', type=str,
                        default='mga_demux_out', help='Folder name to write SADM XML files (default: %(default)s)')
    parser.add_argument('-b', '--bits_per_sample', type=int,
                        default=0, help='Bit depth from MGA Essence Descriptor')
    parser.add_argument('-c', '--channels', type=int,
                        default=0, help='Number of channels from MGA Essence Descriptor')
    parser.add_argument('-s', '--samplerate', type=int,
                        default=0, help='Sampling Rate from MGA Essence Descriptor')

    parser.add_argument('--debug', action='store_const', const=True,
                        default=False, help='Enables debug mode (default: %(default)s)')
    args = parser.parse_args()

    if args.input_mga_file is None:
        raise ValueError('Error: no intput MGA filename')

    filename = args.input_mga_file.name
    filename_stem, filename_ext = os.path.splitext(filename)
    audio_info_xml_filename = filename_stem + ".audio_info.xml"
    mga_file = mga.mga_file.MGAFile(filename, 'r')

    mga_file_info = mga_file.get_info()
    if mga_file_info is None:
        raise Exception('Error: Input MGA file is invalid')

    # Start with MGA values as the default
    # override first with XML file and then switches
    bits_per_sample = mga_file_info.bits_per_sample
    samplerate = mga_file_info.samplerate
    channels = mga_file_info.channels

    if os.path.exists(audio_info_xml_filename):
        print("Using ", audio_info_xml_filename)
        tree = Et.parse(audio_info_xml_filename)
        root = tree.getroot()
#        for child in root:
#            print(child.tag, child.attrib)
        xml_channels = root.find('channels')
        xml_bits_per_sample = root.find('bitDepth')
        xml_samplerate = root.find('samplingRate')
        if (xml_channels == None):
            print("Warning: Audio channel information missing from ", audio_info_xml_filename)
        else:
            channels = int(xml_channels.text)
        if (xml_bits_per_sample == None):
            print("Warning: Bit depth information missing from ", audio_info_xml_filename)
        else:
            bits_per_sample = int(xml_bits_per_sample.text)
        if (xml_samplerate == None):
            print("Warning: Sample rate information missing from ", audio_info_xml_filename)
        else:
            samplerate = int(xml_samplerate.text)
    else:
        print("Warning: audio_info.xml not found, using audio information from S-ADM as a backup")
        print("If the audio information in the S-ADM was not present or varies dynamically then the audio may be corrupted")

    # Check for command line flags which overwrite any previously found values
    if args.bits_per_sample > 0:
        bits_per_sample = args.bits_per_sample
    if args.channels > 0:
        channels = args.channels
    if args.samplerate > 0:
        samplerate = args.samplerate


    if channels == 0:
        raise Exception('Unable to determine number of audio chanels')
    if samplerate == 0:
        raise Exception('Unable to determine audio sampling rate')
    if bits_per_sample == 0:
        raise Exception('Unable to determine audio bit depth')

    if samplerate != 48000:
        raise Exception('Invalid sample rate, only 48kHz supported')

    if bits_per_sample == 16:
        mga_audio_subtype = 'PCM_16'
    elif bits_per_sample == 24:
        mga_audio_subtype = 'PCM_24'
    else:
        raise Exception('Error: Audio in MGA file uses an unsupported bit depth, only 16 & 24 bit supported')

    if args.output_audio_wav is None:
        raise ValueError('Error: no intput MGA filename')
    try:
        audio_wav_file = sf.SoundFile(args.output_audio_wav.name, 'w', samplerate,
                                      channels, mga_audio_subtype, 'LITTLE',
                                      'WAV')  # little endian wave file
    except sf.SoundFileError as e:
        raise sf.SoundFileError("Error: Unable to open audio output file", e, e.args)

    if not os.path.exists(args.output_sadm_xml_folder):
        os.mkdir(args.output_sadm_xml_folder)        


    last_sadm_xml_frame = ''
    print("Reading ", filename, '...')
    print("Bit Depth: ", bits_per_sample)
    print("Number of Audio Channels", channels)
    print("Sample Rate: ", samplerate)
    start_time = time.time()
    frame_no = 1
    while not mga_file.eof():
        # Update S-ADM frame counter and update (compress) metadata payload for this frame
        time_code = mga_file.get_time_code()
        # time code typically uses colon as seperator which won't work in a filename
        time_code_no_colon = time_code.replace(':', '-')
        audio_frame_bytes, sadm_xml_frames = mga_file.read()

        # Check to see if the S-ADM we have is a new one
        # If so create a new file in folder
        for sadm_xml in sadm_xml_frames:
            if sadm_frame_compare(sadm_xml, last_sadm_xml_frame):
                output_xml_file_name = os.path.join(args.output_sadm_xml_folder, time_code_no_colon + '.xml')
                f = open(output_xml_file_name, 'wb')
                f.write(sadm_xml)
                f.close()
                last_sadm_xml_frame = sadm_xml

        if len(audio_frame_bytes) > 0:
            if bits_per_sample == 16:
                audio_frame = np.frombuffer(audio_frame_bytes, dtype=np.dtype(np.int16).newbyteorder('<'))
                audio_frame = audio_frame.reshape(int(len(audio_frame_bytes) / (2 * channels)), channels)
            elif bits_per_sample == 24:
                audio_frame = convert_bytes_to_24bit_np_array(audio_frame_bytes, channels)
            else:
                raise Exception('Error: Audio in MGA file uses an unsupported bit depth, only 16 & 24 bit supported')
            if audio_frame is None:
                raise Exception('Error: Bad Audio frame detected')
            else:
                audio_wav_file.write(audio_frame)

        # print progress
        percent_complete = (mga_file.get_bytes_processed() / mga_file_info.file_size) * 100
        time_elapsed = time.time() - start_time
        time_remaining = ((100 - percent_complete) / percent_complete) * time_elapsed
        time_remaining_str = time.strftime("%H:%M:%S", time.gmtime(time_remaining))
        sys.stdout.write("\rCompleted " + str(int(percent_complete)) + "%,  Time Remaining " + time_remaining_str)
        frame_no = frame_no + 1
    if args.debug:
        mga_file.print_debug()
    mga_file.close()
    audio_wav_file.close()
    print("\nMGA File successfully demuxed")


if __name__ == '__main__':
    main()
