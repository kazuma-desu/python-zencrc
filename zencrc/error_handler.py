"""Error handling utilities for ZenCRC CLI.

This module provides standardized error handling for the ZenCRC command-line interface.
"""

import click


class ErrorHandler:
    """Standardized error handling for the ZenCRC CLI.
    
    This class provides methods for displaying consistent error messages
    and handling common error scenarios throughout the application.
    """
    
    @staticmethod
    def show_no_files_error():
        """Display error when no valid files are found to process."""
        click.echo(click.style("\n❌ Error: No valid files found to process", fg='red'), err=True)
        click.echo("\nUse " + click.style("-r", fg='green') + " flag to search recursively")
        click.echo("\nFor more information, run: " + click.style("zencrc --help", fg='blue') + "\n")
        raise click.Abort()
    
    @staticmethod
    def show_error(message):
        """Display a generic error message.
        
        Args:
            message: The error message to display
        """
        click.echo(click.style(f"\n❌ Error: {message}", fg='red'), err=True)
        raise click.Abort()
    
    @staticmethod
    def verify_create_conflict():
        """Raise error when both --verify and --create are used."""
        raise click.UsageError("Cannot use both --verify and --create")
    
    @staticmethod
    def recurse_with_verify():
        """Raise error when --recurse is used with --verify."""
        raise click.UsageError("--recurse cannot be used with --verify")
    
    @staticmethod
    def files_with_verify():
        """Raise error when additional files are specified with --verify."""
        raise click.UsageError("Additional files cannot be specified with --verify")
    
    @staticmethod
    def verify_requires_sfv():
        """Raise error when --verify is used with a non-SFV file."""
        raise click.UsageError("--verify requires an .sfv file")
    
    @staticmethod
    def create_requires_files():
        """Raise error when --create is used without input files."""
        raise click.UsageError("--create requires input files")
    
    @staticmethod
    def create_requires_sfv():
        """Raise error when --create is used with a non-SFV file."""
        raise click.UsageError("--create requires an .sfv output file")
