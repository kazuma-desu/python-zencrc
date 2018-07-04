## ZenCRC

A command-line tool for CRC32 stuff.


## Installation

This program is packaged as a python package using setuptools and can be installed using `pip` or `pipsi`.
For extended testing running in a virtualenv might be a good idea.

In package directory, run:

    $ pipsi install .

or:

    $ pip install .


`pipsi` is a great alternative to regular pip Hereas it installs each package you install, in an isolated area.
Adn it doesn't require sudo or Admin access to work it's magic.
More detailed functionality can be found @ [pipsi github repo](https://github.com/mitsuhiko/pipsi#readme).


## Usage

This section will explain all the functions and options available in ZenCRC:

# Basic help:

    $ zencrc --help

A more concise version of this help can be hound by using the `--help` or `-h` option.


# Append Mode

	$ zencrc -a {file}

You can append a CRC32 checksum to a filename by using the `--append` or `-a` option.
Takes a positional argument {file} or {files} at the end of the command.
The CRC will be appended to the end of the file in the following format:

	filename.ext --> filename [CRC].ext

So, therefore:
	$ zencrc -a [LNS]Gin no Saji [720p-BD-AAC].mkv
	
will return:	 
	[LNS]Gin no Saji [720p-BD-AAC] [72A89BC1].mkv

Currently no functionality exists to change the format in which the CRC is appended but will be added in v0.9


# Verify Mode

	$ zencrc -v {file}

You can verify a CRC32 checksum in a filename by using the `--verify` or `-v` option.
Takes a positional argument {file} or {files} at the end of the command.
This will calculate the CRC32 checksum of a file, check it against the CRC in the filename of said file,
output the status of that file and the CRC that the program calculated.
If the filename does not contain a CRC the program will still calculate and output the CRC32 of that file.
Currently no functionality exists to only check files with a CRC32 in their name (except some convoluted, yet clever, regex)
but such funtionality may be added in future versions.

