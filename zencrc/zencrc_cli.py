#!/usr/bin/python

# SFV Master ver 1.0 Beta

import os
import argparse
from zencrc import crc32


def expand_dirs(dirlist):
    master_filelist = []
    for i in dirlist:
        if os.path.isdir(i):
            for parent_dir, _, files in os.walk(i):
                for i in range(len(files)):
                    file_path = os.path.join(parent_dir, files[i])
                    master_filelist.append(file_path)
        else:
            master_filelist.append(i)
    return master_filelist


def main():
    parser = argparse.ArgumentParser(description='ZenCRC ver 0.8 Beta')

    parser.add_argument('-a',
                        '--append',
                        action='store_true',
                        help='append CRC32 to file(s)')

    parser.add_argument('-v',
                        '--verify',
                        action='store_true',
                        help='verify CRC32 in file(s)')

    parser.add_argument('-s',
                        '--sfv',
                        help='Create a .sfv file')

    parser.add_argument('-c',
                        '--checksfv',
                        action='store_true',
                        help='Verify a .sfv file')

    parser.add_argument('-r',
                        '--recurse',
                        action='store_true',
                        help='Run program recursively')

    parser.add_argument('file', nargs='+', help='Input File')

    args = parser.parse_args()

    filelist = args.file

    if args.recurse:
        filelist = expand_dirs(filelist)

    if args.verify:
        try:
            print('Verify Mode:\n')
            print('{:50s}{:20s}{:8s}'.format('Filename', 'Status', 'CRC32'))
            for i in filelist:
                if os.path.isdir(i):
                    continue
                else:
                    crc32.verify_in_filename(i)
        except FileNotFoundError as err:
            print(err)

    if args.append:
        try:
            print('Append Mode:')
            for i in filelist:
                if os.path.isdir(i):
                    continue
                else:
                    crc32.append_to_filename(i)
        except FileNotFoundError:
            pass

    if args.sfv:
        crc32.create_sfv_file(args.sfv, filelist)

    if args.checksfv:
        try:
            for i in filelist:
                crc32.verify_sfv_file(i)
        except IsADirectoryError as err:
            print(err)


if (__name__ == '__main__'):
        main()
