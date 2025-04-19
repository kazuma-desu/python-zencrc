import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Union, Iterable

import click
from zencrc import crc32
from zencrc import __version__
from zencrc.error_handler import ErrorHandler

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


@click.group()
def cli():
    """ZenCRC: CRC32 file utility.

    A command-line tool for working with CRC32 checksums in filenames and SFV files.
    """
    pass

@cli.command()
@click.argument('files', nargs=-1, required=True, type=click.Path())
@click.option('-r', '--recurse', is_flag=True, help='Run program recursively')
def verify(files: Tuple[str, ...], recurse: bool) -> None:
    """Verify CRC32 checksums in filenames"""
    filelist = list(files)

    if recurse:
        filelist = expand_dirs(filelist)

    filelist = [path for path in filelist if not Path(path).is_dir()]

    if not filelist:
        ErrorHandler.show_no_files_error()
    else:
        process_verify_mode(filelist)

@cli.command()
@click.argument('files', nargs=-1, required=True, type=click.Path())
@click.option('-r', '--recurse', is_flag=True, help='Run program recursively')
def append(files: Tuple[str, ...], recurse: bool) -> None:
    """Append CRC32 checksums to filenames"""
    filelist = list(files)

    if recurse:
        filelist = expand_dirs(filelist)

    filelist = [path for path in filelist if not Path(path).is_dir()]
    print(filelist)

    if not filelist:
        ErrorHandler.show_no_files_error()
    else:
        process_append_mode(filelist)

def validate_sfv_params(ctx, param, value):
    """Validate SFV command parameters."""
    # Get all parameter values from context
    params = ctx.params
    files = params.get('files', ())
    create = params.get('create')
    verify = params.get('verify')
    recurse = params.get('recurse')

    # Verify mode validation
    if verify:
        if create:
            ErrorHandler.verify_create_conflict()
        if recurse:
            ErrorHandler.recurse_with_verify()
        if files:
            ErrorHandler.files_with_verify()
        if Path(verify).suffix.lower() != '.sfv':
            ErrorHandler.verify_requires_sfv()

    # Create mode validation
    if create:
        if not files:
            ErrorHandler.create_requires_files()
        if Path(create).suffix.lower() != '.sfv':
            ErrorHandler.create_requires_sfv()

    return value

@cli.command()
@click.argument('files', nargs=-1, required=False, type=click.Path(exists=True))
@click.option('-v', '--verify', type=click.Path(exists=True),
              help='Verify SFV file',
              callback=validate_sfv_params)
@click.option('-c', '--create', type=click.Path(),
              help='Create SFV file',
              callback=validate_sfv_params)
@click.option('-r', '--recurse', is_flag=True,
              help='Run program recursively (only with --create)')
def sfv(files: Tuple[str, ...], create: Optional[str], verify: Optional[str], recurse: bool) -> None:
    """Handle SFV file operations.

    Create or verify SFV files. When creating, input files must be provided.
    When verifying, only the SFV file is needed.

    Examples:
    \b
    Create SFV:  zencrc sfv -c checksums.sfv file1.txt file2.txt
    Create SFV recursively:  zencrc sfv -c checksums.sfv . -r
    Verify SFV:  zencrc sfv -v checksums.sfv
    """
    try:
        if verify:
            process_verify_sfv([verify])
        elif create:
            filelist = list(files)
            if recurse:
                filelist = expand_dirs(filelist)
            filelist = [path for path in filelist if not Path(path).is_dir()]
            if not filelist:
                ErrorHandler.show_no_files_error()
            process_create_sfv(create, filelist)
    except Exception as e:
        ErrorHandler.show_error(str(e))


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
