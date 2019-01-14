#!/usr/bin/python3

# copypl - Copies files referenced by an m3u/m3u8/pls playlist.
# Copyright (C) 2019 David Gasaway
# https://bitbucket.org/dgasaway/copypl

# This program is free software; you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program; if not,
# see <http://www.gnu.org/licenses>.

import sys
import os
import shutil
import argparse
import re
import traceback
import time
from urllib.parse import urlparse
from argparse import ArgumentParser
from copypl._version import __version__

# --------------------------------------------------------------------------------------------------
class ApplicationError(Exception): pass

# --------------------------------------------------------------------------------------------------
class ToggleAction(argparse.Action):
    """
    An argparse Action that will convert a y/n arg value into True/False.
    """
    def __call__(self, parser, ns, values, option_string):
        setattr(ns, self.dest, True if values[0] == 'y' else False)

# --------------------------------------------------------------------------------------------------
_maxrc = 0
def warn(msg, rc=1):
    """ Print a message to stderr and record a maximum return code. """
    global _maxrc
    print(msg, file=sys.stderr)
    _maxrc = rc if _maxrc < rc else _maxrc

# --------------------------------------------------------------------------------------------------
def is_contained(root_folder, test_path):
    """
    Determine whether test_path (folder or file) is contained in root_folder or a subfolder.
    """
    # This was created to substitue for os.path.commonpath() which is Python 3.5+ only.  With
    # commonpath(), you can simply check if the result is equal to the root folder.
    root_folder = (root_folder if root_folder.endswith(os.sep) else root_folder + os.sep)
    return os.path.commonprefix([root_folder, test_path]) == root_folder

# --------------------------------------------------------------------------------------------------
def copy_file(src_path, dst_path, args):
    """
    Copy a file from src_path (full path, including file name) to dst_path (full path, including
    file name) with overwrite if a destination file exists with an older modified time; return
    whether copy operation was successful.
    """
    if args.verbose > 1:
        print('    Source:\t\t', src_path)
    if args.verbose > 0 or args.pretend:
        print('    Destination:\t', dst_path)
    
    # Check for bad source or destination conditions.
    if not os.path.isfile(src_path):
        warn('WARNING: unable to locate the following source file')
        warn('    ' + src_path)
        return False
    if os.path.exists(dst_path) and not os.path.isfile(dst_path):
        warn('WARNING: unable to overwrite non-file object in destination; file skipped')
        warn('    ' + src_path)
        return False
    
    # Check for creation of destination subfolder(s).
    dst_folder = os.path.dirname(dst_path)
    if not os.path.isdir(dst_folder):
        if args.verbose > 1:
            print('    Create destination folder: ', dst_folder)
        if not args.pretend:
            os.makedirs(dst_folder)
    
    # Check whether the copy operation is needed.
    do_copy = True
    if not args.ignore_mtime and os.path.exists(dst_path):
        # Check mtime for overwriting existing files.
        src_mtime = os.path.getmtime(src_path)
        dst_mtime = os.path.getmtime(dst_path)
        if dst_mtime == src_mtime:
            do_copy = False
            if args.verbose > 1:
                print('    Modification timestamps match; do nothing')
        elif dst_mtime > src_mtime:
            do_copy = False
            warn('WARNING: destination file is newer than source file; file skipped')
            warn('    ' + src_path)
        else:
            if args.verbose > 1:
                print('    Destination file is older; overwrite')

    if do_copy and not args.pretend:
        shutil.copy2(src_path, dst_path)
    return True

# --------------------------------------------------------------------------------------------------
def copy_entry(entry, src_base_folder, dst_base_folder, args):
    """
    Copy a file and associated extras to the destination.
    """
    if args.verbose > 0:
        print('Processing entry: ', entry)

    # Disallow a URL or other network path.
    url = urlparse(entry)
    if url.scheme != '' or url.netloc != '':
        warn('WARNING: only local files are supported; entry skipped')
        warn('    ' + entry)
        return
    
    # Note that ntpath with swap slashes of either input itself, so we can leave entry as-is.
    entry_norm = entry
    if os.sep == '/':
        item_norm = entry.replace('\\', '/')

    # For sanity and security sake, do not allow paths that would escape the destination folder.
    # Note: Was using os.path.commonpath, but it is 3.5+ only.  For commonprefix to work as intended
    # here, there must be a trailing separator at the end of src_base_folder.  This hack is a bit
    # ugly and depends on the fact it's known the argument will not have a trailing separator.
    src_path = os.path.abspath(os.path.join(src_base_folder, item_norm))
    if not is_contained(src_base_folder, src_path):
        warn('WARNING: file to be copied must be in or below the folder containing the '
              'playlist; entry skipped')
        warn('    ' + entry)
        return
    
    # Get destination path using source path relative to source root.
    dst_path = os.path.join(dst_base_folder, os.path.relpath(src_path, src_base_folder))
    if not copy_file(src_path, dst_path, args):
        return
    
    # Look for extra files.
    src_folder = os.path.dirname(src_path)
    dir_entries = [os.path.join(src_folder, entry) for entry in os.listdir(src_folder)]
    for dir_entry in dir_entries:
        if os.path.isfile(dir_entry) and os.path.splitext(dir_entry)[1].lower() in args.extras:
            # As for normal files, get a destination path using source relative path.
            src_path = os.path.abspath(dir_entry)
            dst_path = os.path.join(dst_base_folder, os.path.relpath(src_path, src_base_folder))
            copy_file(src_path, dst_path, args)

# --------------------------------------------------------------------------------------------------
def copy_m3u_playlist(src_base_folder, dst_base_folder, args):
    """
    Copy files referenced by m3u/m3u8 playlist according to command-line arguments args.
    """
    # Copy entries in the playlist and associated extras.
    ext = os.path.splitext(args.playlist)[1].lower()
    encoding = ('utf-8-sig' if ext == '.m3u8' else 'windows-1252')
    with open(args.playlist, 'r', encoding=encoding) as playlist:
        for entry in [e.strip() for e in playlist if len(e.strip()) > 0 and e[0] != '#']:
            copy_entry(entry, src_base_folder, dst_base_folder, args)

# --------------------------------------------------------------------------------------------------
def copy_pls_playlist(src_base_folder, dst_base_folder, args):
    """
    Copy files referenced by pls playlist according to command-line arguments args.
    """
    # Copy entries in the playlist and associated extras.
    with open(args.playlist, 'r', encoding='utf-8-sig') as playlist:
        for entry in [e.strip() for e in playlist if len(e.strip()) > 0]:
            match = re.match(r'^File\d+=(.+)$', entry)
            if match:
                copy_entry(match.group(1), src_base_folder, dst_base_folder, args)

# --------------------------------------------------------------------------------------------------
def copy_playlist(args):
    """
    Copy files referenced by playlist according to command-line arguments args.
    """
    # Copy entries in the playlist and associated extras.
    src_base_folder = os.path.abspath(os.path.dirname(args.playlist))
    dst_base_folder = os.path.abspath(args.dest)
    ext = os.path.splitext(args.playlist)[1].lower()
    if ext == '.pls':
        copy_pls_playlist(src_base_folder, dst_base_folder, args)
    else:
        copy_m3u_playlist(src_base_folder, dst_base_folder, args)
    
    # Copy the playlist itself.
    if args.copy_playlist:
        if args.verbose > 0:
            print('Processing playlist', args.playlist)
        src_path = os.path.abspath(args.playlist)
        dst_path = os.path.join(dst_base_folder, os.path.relpath(src_path, src_base_folder))
        copy_file(src_path, dst_path, args)

# --------------------------------------------------------------------------------------------------
def main():
    """
    Parse command line argument and initiate copy operations.
    """
    parser = ArgumentParser(
        description='Copies files referenced by an m3u/m3u8/pls playlist, along with selected ' +
        'associated files, while retaining the source folder structure in the destination.',
        fromfile_prefix_chars='@')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-v', '--verbose',
        help='verbose output (can be specified up to three times)',
        action='count', default=0)
    parser.add_argument('--pretend',
        help='output what would be copied to the destination, without any actual copy operations',
        action='store_true', default=False)
    parser.add_argument('-e', '--extra-extension',
        help='file extension of extra files present in source folders to copy to the ' + 
        'destination; can be specified more than once for multiple extensions ' +
        '[default=jpg,jpeg,png]',
        metavar='EXTENSION',
        action='append', dest='extras', default=[])
    parser.add_argument('-c', '--copy-playlist',
        help='copy source playlist file [default=y]',
        action=ToggleAction, choices=['y', 'n'], default=True)
    parser.add_argument('--ignore-mtime',
        help='ignore modification timestap, always overwrite',
        action='store_true', default=False)

    parser.add_argument('playlist',
        help='m3u/m3u8/pls playlist file',
        metavar='playlist_file', action='store')

    parser.add_argument('dest',
        help='destination root folder',
        metavar='destination_folder', action='store')
    args = parser.parse_args()

    # Check for a valid playlist file.
    if not os.path.isfile(args.playlist):
        parser.error('playlist file does not exist: ' + args.playlist)
    if not os.path.splitext(args.playlist)[1].lower() in ['.m3u', '.m3u8', '.pls']:
        parser.error('only m3u, m3u8, and pls playlists are suppored')

    # Check for a valid folder.
    if not os.path.isdir(args.dest):
        parser.error('destination path does not exist: ' + args.dest)

    # Set default extras extensions if user did not specify any.
    if not args.extras:
        args.extras = ['jpg','jpeg','png']

    # Give all the extras extensions a starting period.
    args.extras = [ext.lower() if ext[0] == '.' else '.' + ext.lower() for ext in args.extras]

    if args.verbose > 1:
        print(args)

    # Perform the copy.
    try:
        copy_playlist(args)
    except Exception as e:
        warn('An exception occurred: ' + str(e), rc=2)
        traceback.print_exc(file=sys.stderr)
        exit(_maxrc)
    exit(_maxrc)

# --------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
