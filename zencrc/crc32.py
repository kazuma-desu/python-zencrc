#!/usr/bin/env python3

import os
import re
import binascii
from os.path import splitext
from datetime import datetime

# Global Var
crc_regex = r".*(\[|\()([0-f]{8})(\]|\))[^/]*"


class FileObj:
    pass


def CRC32_from_file(file):
    with open(file, 'rb') as temp:
        temp = (binascii.crc32(temp.read()) & 0xFFFFFFFF)
        return "%08X" % temp


def verify_in_filename(files):
    try:
        filename = str(files[files.rfind("/") + 1:])
        filename = filename[0:42] + '...'
        filename_crc = re.search(crc_regex, files, re.I)
        filename_crc = str.upper(filename_crc.group(2))
        current = CRC32_from_file(files)
        if (filename_crc == current):
            status = 'File Ok'
        else:
            status = 'File Corrupt'
        print('{:47s} {:22s}{:8s}'.format(filename,
                                          status,
                                          current))
    except AttributeError as err:
        status = 'No CRC32 in filename'
        current = CRC32_from_file(files)
        print('{:47s} {:22s}{:8s}'.format(filename,
                                          status,
                                          current))
    except FileNotFoundError as err:
        print(err)


def append_to_filename(file_in):
    _, ext = os.path.splitext(file_in)
    if ext != '.sfv':
        try:
            already_appended = re.search(crc_regex, file_in, re.I)
            if already_appended:
                print(file_in[file_in.rfind("/") + 1:],
                      ': already contains a CRC32 in file name.')
                return file_in
            else:
                print('{} ...'.format(file_in))
                crc = CRC32_from_file(file_in)
                basename, ext = splitext(file_in)
                os.rename(file_in, '{} [{}]{}'.format(basename, crc, ext))
                new_filename = ('{} [{}]{}'.format(basename, crc, ext))
                print(crc + ' Done')
                return new_filename
        except FileNotFoundError:
            print('No such file or directory:', file_in)
    else:
        return file_in


def remove_from_filename(file_in):
    try:
        regex = re.compile(r"(\s?\[|\s?\()([0-f]{8})(\]|\))", re.I)
        filename_crc = re.search(regex, file_in)
        new_filename = file_in.replace(filename_crc.group(0), '')
        os.rename(file_in, new_filename)
    except AttributeError:
        print('{} has no CRC32 to remove'.format(file_in))


def verify_sfv_file(file_in):
    with open(file_in, 'r') as f:
        text = f.read().split('\n')
        total_files = ok_files = corrupt = not_found = 0
        for line in text:
            line = line.rstrip()
            if(len(line) != 0 and line[0] != ';'):
                crc = line[line.rfind(" ") + 1:]
                cur_file = line[0:-9]
                total_files += 1
                try:
                    calc_crc = str.upper(CRC32_from_file(cur_file))
                    if(calc_crc == crc.upper()):
                        cur_file = cur_file[cur_file.rfind('/') + 1:]
                        print('{}:\nFile OK\n'.format(cur_file))
                        ok_files += 1
                    else:
                        cur_file = cur_file[cur_file.rfind('/') + 1:]
                        print('{}:\nCorrupt file\n'.format(cur_file))
                        corrupt += 1
                except FileNotFoundError:
                    print(cur_file + ':')
                    print('No such file or directory: {}'.format(cur_file))
                    not_found += 1
        print('\nSummary:\n Total - {}\n'.format(total_files),
              'OK - {}\n'.format(ok_files),
              'Corrupt - {}\n'.format(corrupt),
              'Not Found - {}'.format(not_found))


def create_sfv_file(sfv_filename, in_files):
    print('Creating {}...'.format(sfv_filename))
    with open(sfv_filename, encoding='utf-8', mode='w+') as buf:
        ctime = datetime.now().strftime('%A, %d %B %Y @ %I:%M %p')
        nline = '\n;'
        char = 'charset=UTF-8'
        hasht = 'Hash type: CRC-32'
        head = '; Created by SFV Master 1.2{1} {0}{1} {2}{1} {3}{1}\n'.format(
            ctime,
            nline,
            char,
            hasht)

        buf.write(head)
        for fname in in_files:
            _, ext = os.path.splitext(fname)
            if(ext != '.sfv'):
                try:
                    file_crc = CRC32_from_file(fname)
                    buf.write('{} {}\n'.format(fname, file_crc))
                except IsADirectoryError:
                    pass
            else:
                pass
    print('Done')
