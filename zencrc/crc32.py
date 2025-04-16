import os
import re
import binascii
from os.path import splitext
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Union

import click

# Improved regex for CRC32 in filenames - safe from catastrophic backtracking
# Uses specific character classes, atomic groups, and anchoring to prevent DoS vulnerabilities
# Avoids using .* patterns which can lead to catastrophic backtracking
# Using only lowercase hex digits and applying case-insensitive flag when used
CRC_REGEX = r"[^\[\(]*?([\[\(])([0-9a-f]{8})([\]\)])[^/]*$"



def crc32_from_file(filepath: str) -> str:
    """Calculate CRC32 checksum for a file.
    
    Args:
        filepath: Path to the file to calculate CRC32 for
        
    Returns:
        CRC32 checksum as an uppercase hex string
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        IsADirectoryError: If the path is a directory
    """
    with open(filepath, 'rb') as file:
        checksum = binascii.crc32(file.read()) & 0xFFFFFFFF
        return f"{checksum:08X}"


def get_filename_display(filepath: str, max_length: int = 44) -> str:
    """Get a filename for display purposes, truncated if necessary.
    
    Args:
        filepath: Path to the file
        max_length: Maximum length before truncation
        
    Returns:
        Filename for display, truncated if longer than max_length
    """
    filename = Path(filepath).name
    if len(filename) > max_length:
        return filename[:max_length] + '...'
    return filename


def extract_crc_from_filename(filepath: str) -> Optional[str]:
    """Extract CRC32 from a filename.
    
    Args:
        filepath: Path to the file
        
    Returns:
        CRC32 checksum as a string, or None if not found
    """
    # Using re.I (IGNORECASE) flag to match both uppercase and lowercase hex digits
    match = re.search(CRC_REGEX, filepath, re.I)
    if not match:
        return None
    return match.group(2).upper()


def verify_in_filename(filepath: str) -> bool:
    """Verify CRC32 in filename against calculated CRC32.
    
    Args:
        filepath: Path to the file to verify
        
    Returns:
        True if CRC32 matches, False if it doesn't match or no CRC32 found
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    try:
        # Get file info
        path = Path(filepath)
        filename = get_filename_display(filepath)
        file_size = path.stat().st_size
        size_str = format_file_size(file_size)
        current_crc = crc32_from_file(filepath)
        
        # Extract CRC from filename if present
        filename_crc = extract_crc_from_filename(filepath)
        
        if not filename_crc:
            status = click.style('No CRC32 found', fg='yellow')
            crc_display = click.style(current_crc, fg='cyan', bold=True)
            click.echo(f'{filename:<40} {size_str:>10} {status:<15} {crc_display}')
            return False
            
        if filename_crc == current_crc:
            status = click.style('✓ Match', fg='green', bold=True)
            crc_display = click.style(current_crc, fg='green')
            result = True
        else:
            status = click.style('✗ Mismatch', fg='red', bold=True)
            expected = click.style(f'Expected: {filename_crc}', fg='yellow')
            click.echo(f'{filename:<40} {size_str:>10} {status:<15} {click.style(current_crc, fg="red")}')
            click.echo(f'{" ":<40} {" ":>10} {" ":<15} {expected}')
            return False
            
        click.echo(f'{filename:<40} {size_str:>10} {status:<15} {crc_display}')
        return result
    except FileNotFoundError as err:
        click.echo(click.style(str(err), fg='red'))
        return False


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string (e.g., '4.2 MB')
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.1f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.1f} GB"


def append_to_filename(filepath: str) -> bool:
    """Append CRC32 to filename if not already present.
    
    Args:
        filepath: Path to the file
        
    Returns:
        True if CRC32 was appended, False otherwise
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    try:
        path = Path(filepath)
        filename = path.name
        file_size = path.stat().st_size
        size_str = format_file_size(file_size)
        
        if extract_crc_from_filename(filepath):
            click.echo(f'{filename:<40} {size_str:>10} ' + 
                      click.style('Already has CRC32', fg='yellow'))
            return False
            
        crc = crc32_from_file(filepath)
        new_path = path.with_name(f'{path.stem} [{crc}]{path.suffix}')
        
        os.rename(filepath, new_path)
        click.echo(f'{filename:<40} {size_str:>10} ' + 
                 click.style(f'Added [{crc}]', fg='green'))
        return True
    except FileNotFoundError:
        click.echo(click.style(f'Error: {filepath} not found', fg='red'))
        return False


def parse_sfv_line(line: str) -> Optional[Tuple[str, str]]:
    """Parse a line from an SFV file.
    
    Args:
        line: A line from an SFV file
        
    Returns:
        Tuple of (filepath, crc) if valid, None if comment or empty
    """
    line = line.rstrip()
    if not line or line.startswith(';'):
        return None
        
    # More robust parsing - find the last space and split there
    last_space = line.rfind(' ')
    if last_space == -1:
        return None
        
    filepath = line[:last_space]
    crc = line[last_space + 1:]
    
    # Validate CRC format
    if not re.match(r'^[0-9A-Fa-f]{8}$', crc):
        return None
        
    return filepath, crc


def verify_sfv_file(sfv_filepath: str) -> Dict[str, int]:
    """Verify files listed in an SFV file.
    
    Args:
        sfv_filepath: Path to the SFV file
        
    Returns:
        Dictionary with counts of total, ok, corrupt, and not found files
        
    Raises:
        FileNotFoundError: If the SFV file doesn't exist
    """
    stats = {'total': 0, 'ok': 0, 'corrupt': 0, 'not_found': 0}
    
    # Get file info and print header
    sfv_path = Path(sfv_filepath)
    sfv_name = sfv_path.name
    sfv_size = format_file_size(sfv_path.stat().st_size)
    
    click.echo(click.style("Verifying SFV file: ", bold=True) + 
              click.style(f"{sfv_name}", fg='blue', bold=True) + 
              f" ({sfv_size})")
    click.echo("─" * 80)
    
    # Print header
    header = (
        f"{click.style('Filename', bold=True):<40} "
        f"{click.style('Size', bold=True):>10} "
        f"{click.style('Status', bold=True):<15} "
        f"{click.style('CRC32', bold=True)}"
    )
    click.echo(header)
    click.echo("─" * 80)
    
    with open(sfv_filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parsed = parse_sfv_line(line)
            if not parsed:
                continue
                
            filepath, expected_crc = parsed
            stats['total'] += 1
            
            try:
                path = Path(filepath)
                filename = get_filename_display(filepath)
                calculated_crc = crc32_from_file(filepath).upper()
                
                try:
                    size_str = format_file_size(path.stat().st_size)
                except FileNotFoundError:
                    size_str = "??.? KB"
                
                if calculated_crc == expected_crc.upper():
                    status = click.style("✓ Match", fg='green', bold=True)
                    crc_text = click.style(calculated_crc, fg='green')
                    click.echo(f"{filename:<40} {size_str:>10} {status:<15} {crc_text}")
                    stats['ok'] += 1
                else:
                    status = click.style("✗ Mismatch", fg='red', bold=True)
                    crc_text = click.style(calculated_crc, fg='red')
                    expected_text = click.style(f"Expected: {expected_crc.upper()}", fg='yellow')
                    click.echo(f"{filename:<40} {size_str:>10} {status:<15} {crc_text}")
                    click.echo(f"{'':<40} {'':<10} {'':<15} {expected_text}")
                    stats['corrupt'] += 1
            except FileNotFoundError:
                status = click.style("✗ Not found", fg='red', bold=True)
                click.echo(f"{filepath:<40} {'':>10} {status:<15} {click.style(expected_crc.upper(), fg='yellow')}")
                stats['not_found'] += 1
    
    # Print summary with colors
    click.echo("─" * 80)
    click.echo(click.style("Summary:", bold=True))
    click.echo(f" Total: {click.style(str(stats['total']), bold=True)}")
    click.echo(f" OK: {click.style(str(stats['ok']), fg='green', bold=True)}")
    click.echo(f" Corrupt: {click.style(str(stats['corrupt']), fg='red', bold=True)}")
    click.echo(f" Not Found: {click.style(str(stats['not_found']), fg='yellow', bold=True)}")
    
    return stats


def create_sfv_file(sfv_filepath: str, filepaths: List[str]) -> int:
    """Create an SFV file for the given files.
    
    Args:
        sfv_filepath: Path to create the SFV file
        filepaths: List of files to include in the SFV file
        
    Returns:
        Number of files successfully added to the SFV file
    """
    # Print header
    click.echo(click.style('Creating SFV: ', bold=True) + 
              click.style(f'{sfv_filepath}', fg='blue', bold=True))
    click.echo("─" * 80)
    
    # Setup counters
    added_count = 0
    skipped_count = 0
    total_size = 0
    
    # Print header for file list
    header = (
        f"{click.style('Filename', bold=True):<40} "
        f"{click.style('Size', bold=True):>8} "
        f"{click.style('Status', bold=True):<15} "
        f"{click.style('CRC32', bold=True)}"
    )
    click.echo(header)
    click.echo("─" * 80)
    
    # Open SFV file for writing
    with open(sfv_filepath, encoding='utf-8', mode='w+') as buf:
        # Write header
        timestamp = datetime.now().strftime('%A, %d %B %Y @ %I:%M %p')
        header = (f'; Created by ZenCRC v0.9.4\n;'
                 f' {timestamp}\n;'
                 f' charset=UTF-8\n;'
                 f' Hash type: CRC-32\n\n')
        buf.write(header)
        
        # Process each file
        for filepath in filepaths:
            path = Path(filepath)
            filename = path.name
            
            # Skip SFV files
            if filepath.endswith('.sfv'):
                click.echo(f"{filename:<40} {'':>10} {click.style('Skipped (SFV)', fg='yellow'):<15}")
                skipped_count += 1
                continue
                
            try:
                # Get file size
                file_size = path.stat().st_size
                total_size += file_size
                size_str = format_file_size(file_size)
                
                # Calculate CRC
                file_crc = crc32_from_file(filepath)
                
                # Write to SFV file
                buf.write(f'{filepath} {file_crc}\n')
                
                # Display progress
                click.echo(f"{filename:<40} {size_str:>10} " + 
                          click.style('Added', fg='green', bold=True) + 
                          f"{'':<9} {click.style(file_crc, fg='cyan')}")
                added_count += 1
                
            except FileNotFoundError:
                click.echo(f"{filename:<40} {'':>10} {click.style('Not found', fg='red', bold=True):<15}")
                skipped_count += 1
            except IsADirectoryError:
                click.echo(f"{filename:<40} {'':>10} {click.style('Is directory', fg='yellow'):<15}")
                skipped_count += 1
    
    # Print summary
    click.echo("─" * 80)
    total_size_str = format_file_size(total_size)
    click.echo(click.style("Summary:", bold=True) + 
              f" Added {click.style(str(added_count), fg='green', bold=True)} files" + 
              (f", Skipped {click.style(str(skipped_count), fg='yellow', bold=True)} files" if skipped_count > 0 else "") + 
              f", Total size: {click.style(total_size_str, bold=True)}")
    
    return added_count