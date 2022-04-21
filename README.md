# ZenCRC

A command-line tool for CRC32 stuff.

## Installation

This program is packaged as a python package using setuptools and can be installed using `pip` or `pipsi`.
For extended testing, running in a virtualenv might be a good idea.

In package directory, run:

    $ pipsi install .

or:

    $ pip install .

Or install from PyPI:

    $ pip install zencrc

`pipsi` is a great alternative to regular pip Manily beacause it installs
each package you install, in an isolated area.
Adn it doesn't require sudo or Admin access to work it's magic.
More detailed functionality can be found @ [pipsi github repo](https://github.com/mitsuhiko/pipsi#readme).

## Usage

This section will explain all the functions and options available in ZenCRC:

### Basic help

    $ zencrc --help

A more concise version of this help can be hound by using the `--help` or `-h`
option.

### Append Mode

    $ zencrc -a {file}
    $ zencrc --append {file}

You can append a CRC32 checksum to a filename by using the `--append` or `-a`
option.
Takes a positional argument {file} or {files} at the end of the command.
The CRC will be appended to the end of the file in the following format:

    filename.ext --> filename [CRC].ext

So, therefore:
    $ zencrc -a [LNS]Gin no Saji [720p-BD-AAC].mkv

will return:
    [LNS]Gin no Saji [720p-BD-AAC] [72A89BC1].mkv

Currently no functionality exists to change the format in which the CRC
is appended but will be added in v0.9

### Verify Mode

    $ zencrc -v {file}
    $ zencrc --verify {file}

You can verify a CRC32 checksum in a filename by using the `--verify` or `-v`
option.

Takes a positional argument {file} or {files} at the end of the command.

This will calculate the CRC32 checksum of a file, check it against the CRC
in the filename of said file,
output the status of that file and the CRC that the program calculated.

If the filename does not contain a CRC the program will still calculate
and output the CRC32 of that file.

Currently no functionality exists to only check files with a CRC32 in
their name (except some convoluted, yet clever, regex)
but such funtionality may be added in future versions.

### SFV file out

    $ zencrc -s {file_out.sfv} {file(s)}
    $ zencrc --sfv {file_out.sfv} {file(s)}

You can output the calculated checksums to a .sfv file using this option.

### SFV file in / SFV file verify

    $ zencrc -c {file_out.sfv} {file(s)}
    $ zencrc --check-sfv {file_out.sfv} {file(s)}

You can verify .sfv files using this option.

### Recursion

    $ zencrc -r -{a|v|s|c}

This function ideally would scan directories recursivly and apply the
above-mentioned accordingly, though recursion actually doesnt do anythin
at this point. Either way version 0.9 would most definitely have this function.
__Version 0.9b is already in development__

## Things to expect in the future / Dev notes
__This version refers to version "0.9.1.1b1" from this poin onwards__

### A GUI 
-This is something that I've already been working on since the begining of this project.
 While it is far from complete it is also definitely coming, so there's that.

-Currently in the stage of design.

-Probably will use this CLI tool as the main code base.

### Better CRC manipulation 
-This includes better and more efficent funcions to calculate and implement CRC32 checksums.
-Currently Alpha testing with "zlib" to see which is faster(compared against "binascii").

### Better argument parsing
-This version using argparse works but it also has its quirks, so possible fixes to those.
-Possibly might switch to click in a future version. Possibly.
-Small issue when using some arguments together(like -a & -s) will be fixed in next version

### Cross-platform support
-Non-critical file structure recursion issues in Windows hoping to fix that soon 
