import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Union, Iterable

import click
from click.types import File
from zencrc import crc32
from . import __version__


# Output styling functions
def print_header(title: str) -> None:
    """Print a styled header with the given title.

    Args:
        title: The title to display in the header
    """
    click.echo(click.style('\n╒═══════════════════════════════════════════════════════════════════════════╕', fg='blue'))
    click.echo(click.style('│ ', fg='blue') +
              click.style(title, fg='green', bold=True) +
              click.style(' │', fg='blue').rjust(73))
    click.echo(click.style('╘═══════════════════════════════════════════════════════════════════════════╛', fg='blue'))
    click.echo()


def print_table_header(columns: List[Tuple[str, int, bool]]) -> None:
    """Print a styled table header with the given columns.

    Args:
        columns: List of tuples containing (name, width, align_right)
    """
    header_parts = []
    for name, width, align_right in columns:
        if align_right:
            header_parts.append(f"{click.style(name, bold=True):>{width}}")
        else:
            header_parts.append(f"{click.style(name, bold=True):<{width}}")

    click.echo(' '.join(header_parts))
    click.echo("─" * 80)


def print_footer(processed: int, item_type: str = "files") -> None:
    """Print a styled footer with the number of processed items.

    Args:
        processed: Number of processed items
        item_type: Type of items processed (default: "files")
    """
    if processed > 0:
        click.echo("─" * 80)
        click.echo(click.style(f"Processed {processed} {item_type}", fg='blue'))


def expand_dirs(dirlist: Iterable[str]) -> List[str]:
    """Expand directories in the list to include all files recursively.

    Args:
        dirlist: List of file and directory paths

    Returns:
        List of file paths with directories expanded
    """
    master_filelist = []
    for path_str in dirlist:
        path = Path(path_str)
        if path.is_dir():
            for root, _, files in os.walk(str(path)):
                root_path = Path(root)
                # Add files in batches rather than one by one
                master_filelist.extend(str(root_path / file) for file in files)
        else:
            master_filelist.append(path_str)
    return master_filelist


def process_verify_mode(filelist: List[str]) -> None:
    """Process files in verify mode.

    Args:
        filelist: List of files to process
    """
    try:
        print_header('VERIFY MODE')

        # Print header with better formatting
        print_table_header([
            ('Filename', 40, False),
            ('Size', 10, True),
            ('Status', 15, False),
            ('CRC32', 10, False)
        ])

        # Process files
        processed = 0
        for filepath in filelist:
            path = Path(filepath)
            if path.is_dir():
                continue
            crc32.verify_in_filename(filepath)
            processed += 1

        # Print summary footer
        print_footer(processed)
    except FileNotFoundError as err:
        click.echo(click.style(str(err), fg='red'))


def process_append_mode(filelist: List[str]) -> None:
    """Process files in append mode.

    Args:
        filelist: List of files to process
    """
    try:
        print_header('APPEND MODE')

        # Process files
        processed = 0
        for filepath in filelist:
            path = Path(filepath)
            if path.is_dir():
                continue
            crc32.append_to_filename(filepath)
            processed += 1

        # Print summary footer if files were processed
        print_footer(processed)

    except FileNotFoundError:
        pass


def process_create_sfv(sfv_filepath: str, filelist: List[str]) -> None:
    """Create an SFV file.

    Args:
        sfv_filepath: Path to the SFV file to create
        filelist: List of files to include in the SFV file
    """
    print_header('CREATE SFV')
    crc32.create_sfv_file(sfv_filepath, filelist)


def process_verify_sfv(filelist: List[str]) -> None:
    """Verify SFV files.

    Args:
        filelist: List of SFV files to verify
    """
    try:
        print_header('VERIFY SFV')

        # Process files
        processed = 0
        for filepath in filelist:
            crc32.verify_sfv_file(filepath)
            processed += 1

        # Print summary footer if files were processed
        print_footer(processed, "SFV files")

    except IsADirectoryError as err:
        click.echo(click.style(str(err), fg='red'))


@click.command(help=f'ZenCRC v{__version__}')
@click.argument('files', nargs=-1, required=True, type=click.Path())
@click.option('-a', '--append', is_flag=True, help='Append CRC32 to file(s)')
@click.option('-v', '--verify', is_flag=True, help='Verify CRC32 in file(s)')
@click.option('-s', '--sfv', type=click.Path(), help='Create a .sfv file')
@click.option('-c', '--checksfv', is_flag=True, help='Verify a .sfv file')
@click.option('-r', '--recurse', is_flag=True, help='Run program recursively')
def cli(files: Tuple[str, ...], append: bool, verify: bool, sfv: Optional[str],
       checksfv: bool, recurse: bool) -> None:
    """ZenCRC: CRC32 file utility.

    A command-line tool for working with CRC32 checksums in filenames and SFV files.
    """
    filelist = list(files)

    if recurse:
        filelist = expand_dirs(filelist)

    filelist = [path for path in filelist if not Path(path).is_dir()]

    if filelist:
        if verify:
            process_verify_mode(filelist)

        if append:
            process_append_mode(filelist)

        if sfv:
            process_create_sfv(sfv, filelist)

        if checksfv:
            process_verify_sfv(filelist)
    else:
        click.echo(click.style("\n❌ Error: No valid files found to process", fg='red'), err=True)
        click.echo("\nUse " + click.style("-r", fg='green') + " flag to search recursively")
        click.echo("\nFor more information, run: " + click.style("zencrc --help", fg='blue') + "\n")
        raise click.Abort()

def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
