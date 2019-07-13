#!/usr/bin/env python3
import os
import sys
import argparse
import hashlib


def arg_parse():
    """ Parser for command-line editon
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("SRC_FILE")
    parser.add_argument("DESTINATION")
    return parser.parse_args()
    

def is_exist(src):
    """ Check source file is exist or not
    """
    try:
        os.stat(src)
    except FileNotFoundError:
        print('rsync: link_stat "'+os.path.realpath(src)+'" failed: No such file or directory (2)')
        return False
    return True


def change_same_permission(src, dest):
    """ Change destination file have same permissions with source file
    """
    os.chmod(dest, os.stat(src).st_mode)


def change_same_time(src, dest):
    """ Change destination file have same access time and modified time with source file
    """
    src_info = os.stat(src)
    os.utime(dest, (src_info.st_atime, src_info.st_mtime))


def write_chunks(src, dest, chunk_size=1024):
    """ Write data from source file to destination file
    Data are divide to packets/chunks (1 packet/chunk = 1024 bytes)
    then are write to destination file
    """
    # Open source and destionation file descriptor
    src_fd = os.open(src, os.O_RDONLY)
    dest_fd = os.open(dest, os.O_WRONLY)
    # Write data (per chunk = 1024 bytes) in source file to destination file
    anchor = 0
    while anchor < os.stat(src).st_size:
        os.write(dest_fd, os.read(src_fd, chunk_size))
        anchor += chunk_size
    # Close source and destination file descriptor
    os.close(src_fd)
    os.close(dest_fd)


def create_new_file(path):
    """ Try to create new file with name = path
    """
    if not os.path.exists(path):
        fd = os.open(path, os.O_CREAT)
        os.close(fd)


def copy_file(src, dest):
    """ Copy source file to destination
    If destination file is a file, then do nothing
    If destination file is a directory, then create 
    new file with name = source file inside "dest" directory
    """
    # Check if destination file exist or not, if not, create a new file
    if not os.path.exists(dest):
        create_new_file(dest)
    else:
        if os.path.isdir(dest):
            dest = os.path.join(dest, os.path.basename(src))
            create_new_file(dest)
    write_chunks(src, dest)
    change_same_permission(src, dest)
    change_same_time(src, dest)


def make_symlink(src, dest):
    """ Make symbolic link from source file
    """
    if os.path.isdir(dest):
        dest = os.path.join(dest, os.path.basename(src))
    os.link(src, dest)


def file_to_hashlist(src, chunk_size=1024):
    """ This function return 2 values:
    - 1st value: A list of checksums of source file with each checksum
    is md5 hash value of 1024 bytes of source file.
    - 2nd value: A dictionary with keys are checksums of every 1024 bytes from file and
    every value is 1024 bytes of that checksum
    """
    # Create list and dict for storage
    src_checksum = []
    hashdict_checksum = {}
    # Read source file
    src_fd = os.open(src, os.O_RDONLY)
    pointer = 0
    while pointer < os.stat(src).st_size:
        # Get checksum of 1024 bytes
        h = hashlib.md5()
        content = os.read(src_fd, chunk_size)
        h.update(content)
        checksum = h.hexdigest()
        # Add checksum to containers (list and dict)
        src_checksum.append(checksum)
        hashdict_checksum[checksum] = content
        # Continue pointer for next 1024 bytes
        pointer += chunk_size
    os.close(src_fd)
    return src_checksum, hashdict_checksum


def rolling_checksum(src, dest_checksum, chunk_size=1024):
    """ Rolling checksum algorithm
    This function find differences in source file and destination file by 
    compare checksum of every 1024 bytes in source file with checksum list of
    destination file.
    If it find difference, it appends that difference into instruction list, ortherwise
    it will append checksum into instruction list.
    """
    # Create pointer for file seeking
    pointer = 0
    # First value and last value are index of difference
    first = 0
    last = 0
    # Create container for instruction
    instruction = []
    # Read source file
    src_fd = os.open(src, os.O_RDONLY)
    # Rolling checksum algorithm
    while pointer < os.stat(src).st_size:
        # Get checksum of 1024 bytes
        h = hashlib.md5()
        os.lseek(src_fd, pointer, 0)
        chunk = os.read(src_fd, chunk_size)
        h.update(chunk)
        checksum = h.hexdigest()
        # If checksum of 1024 bytes in list of checksums of destination file
        # check if there's difference data (with last and first value), then add
        # it to instruction list
        # Then add checksum to instruction list
        if checksum in dest_checksum:
            if last > first:
                os.lseek(src_fd, first, 0)
                instruction.append(os.read(src_fd, last-first))
            instruction.append(checksum)
            # Continue increase pointer
            pointer += chunk_size
            # Because I saved difference data, I should increase first value equal to
            # pointer
            first = pointer
        else:
            # If checksum not in list of destination checksum, I should increase pointer
            # and last value by 1 for next checking
            pointer += 1
            last = pointer
    # We have to save lastest data in source file if pointer can't point to
    if last > first:
        os.lseek(src_fd, first, 0)
        instruction.append(os.read(src_fd, last-first))
    return instruction
            

def update_file(src, dest, chunk_size=1024):
    """ Update destination file using rolling checksum algorithm
    After having instruction list from rolling checksum algorithm, this
    function will create a new empty file, write data to new file 
    based on instruction.
    After that, it delete old file (destination file) and replace it
    own name equal to destination file.
    """
    dest_checksum, hashlib_checksum = file_to_hashlist(dest)
    instruction = rolling_checksum(src, dest_checksum)
    temp_name = "dest_temp"
    new_fd = os.open(temp_name, os.O_CREAT | os.O_WRONLY)
    for data in instruction:
        if data in hashlib_checksum.keys():
            os.write(new_fd, hashlib_checksum[data])
        else:
            os.write(new_fd, data)
    os.close(new_fd)
    os.remove(dest)
    os.rename(temp_name, dest)
    change_same_permission(src, dest)
    change_same_time(src, dest)


def main():
    """ Main function
    """
    # Create arguments from argument parser
    args = arg_parse()
    # Get source path and destination path
    src_path = os.path.abspath(args.SRC_FILE)
    dest_path = os.path.abspath(args.DESTINATION)
    # Case processing
    if is_exist(src_path):
        if os.path.islink(src_path):
            make_symlink(src_path, dest_path)
        elif os.path.exists(dest_path):
            update_file(src_path, dest_path)
        else:
            copy_file(src_path, dest_path)


if __name__ == "__main__":
    main()