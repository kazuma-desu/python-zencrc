import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Union, Iterable

import click
from zencrc import crc32


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
            # Use os.walk which is more efficient than path.glob('**/*')
            # for large directory trees
            for root, _, files in os.walk(str(path)):
                root_path = Path(root)
                # Add files in batches rather than one by one
                master_filelist.extend(str(root_path / file) for file in files)
        else:
            master_filelist.append(path_str)
    return master_filelist


@click.command(help='ZenCRC ver 0.9.4')
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

    if verify:
        try:
            click.echo(click.style('\n╒═══════════════════════════════════════════════════════════════════════════╕', fg='blue'))
            click.echo(click.style('│ ', fg='blue') + 
                      click.style('VERIFY MODE', fg='green', bold=True) + 
                      click.style(' │', fg='blue').rjust(73))
            click.echo(click.style('╘═══════════════════════════════════════════════════════════════════════════╛', fg='blue'))
            click.echo()
            
            # Print header with better formatting
            header = (
                f"{click.style('Filename', bold=True):<40} "
                f"{click.style('Size', bold=True):>10} "
                f"{click.style('Status', bold=True):<15} "
                f"{click.style('CRC32', bold=True)}"
            )
            click.echo(header)
            click.echo("─" * 80)
            
            # Process files
            processed = 0
            for filepath in filelist:
                path = Path(filepath)
                if path.is_dir():
                    continue
                crc32.verify_in_filename(filepath)
                processed += 1
                
            # Print summary footer
            if processed > 0:
                click.echo("─" * 80)
                click.echo(click.style(f"Processed {processed} files", fg='blue'))
        except FileNotFoundError as err:
            click.echo(click.style(str(err), fg='red'))

    if append:
        try:
            click.echo(click.style('\n╒═══════════════════════════════════════════════════════════════════════════╕', fg='blue'))
            click.echo(click.style('│ ', fg='blue') + 
                      click.style('APPEND MODE', fg='green', bold=True) + 
                      click.style(' │', fg='blue').rjust(73))
            click.echo(click.style('╘═══════════════════════════════════════════════════════════════════════════╛', fg='blue'))
            click.echo()
            
            # Process files
            processed = 0
            for filepath in filelist:
                path = Path(filepath)
                if path.is_dir():
                    continue
                crc32.append_to_filename(filepath)
                processed += 1
                
            # Print summary footer if files were processed
            if processed > 0:
                click.echo("─" * 80)
                click.echo(click.style(f"Processed {processed} files", fg='blue'))
                
        except FileNotFoundError:
            pass

    if sfv:
        click.echo(click.style('\n╒═══════════════════════════════════════════════════════════════════════════╕', fg='blue'))
        click.echo(click.style('│ ', fg='blue') + 
                  click.style('CREATE SFV', fg='green', bold=True) + 
                  click.style(' │', fg='blue').rjust(73))
        click.echo(click.style('╘═══════════════════════════════════════════════════════════════════════════╛', fg='blue'))
        click.echo()
        
        crc32.create_sfv_file(sfv, filelist)

    if checksfv:
        try:
            click.echo(click.style('\n╒═══════════════════════════════════════════════════════════════════════════╕', fg='blue'))
            click.echo(click.style('│ ', fg='blue') + 
                      click.style('VERIFY SFV', fg='green', bold=True) + 
                      click.style(' │', fg='blue').rjust(73))
            click.echo(click.style('╘═══════════════════════════════════════════════════════════════════════════╛', fg='blue'))
            click.echo()
            
            # Process files
            processed = 0
            for filepath in filelist:
                crc32.verify_sfv_file(filepath)
                processed += 1
                
            # Print summary footer if files were processed
            if processed > 0:
                click.echo("─" * 80)
                click.echo(click.style(f"Processed {processed} SFV files", fg='blue'))
                
        except IsADirectoryError as err:
            click.echo(click.style(str(err), fg='red'))


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
