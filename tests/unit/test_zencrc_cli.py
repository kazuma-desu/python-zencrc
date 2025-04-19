"""
Unit tests for the zencrc.zencrc_cli module.
"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import click
from click.testing import CliRunner

from zencrc import crc32
from zencrc.zencrc_cli import cli, expand_dirs


class TestExpandDirs(unittest.TestCase):
    """Test cases for the expand_dirs function."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Create a subdirectory
        self.sub_dir = self.test_dir / "subdir"
        self.sub_dir.mkdir()
        
        # Create test files
        self.test_file1 = self.test_dir / "file1.txt"
        self.test_file1.write_text("File 1 content")
        
        self.test_file2 = self.test_dir / "file2.txt"
        self.test_file2.write_text("File 2 content")
        
        # Create a file in the subdirectory
        self.sub_file = self.sub_dir / "subfile.txt"
        self.sub_file.write_text("Subfile content")

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_expand_dirs_with_files(self):
        """Test expand_dirs with file paths."""
        # Test with a list of files
        file_list = [str(self.test_file1), str(self.test_file2)]
        result = expand_dirs(file_list)
        
        # Should return the same list since there are no directories
        self.assertEqual(set(result), set(file_list))

    def test_expand_dirs_with_directory(self):
        """Test expand_dirs with a directory path."""
        # Test with a directory
        dir_list = [str(self.test_dir)]
        result = expand_dirs(dir_list)
        
        # Should return all files in the directory and subdirectories
        expected_files = {
            str(self.test_file1),
            str(self.test_file2),
            str(self.sub_file)
        }
        self.assertEqual(set(result), expected_files)

    def test_expand_dirs_mixed(self):
        """Test expand_dirs with a mix of files and directories."""
        # Test with a mix of files and directories
        mixed_list = [str(self.test_file1), str(self.sub_dir)]
        result = expand_dirs(mixed_list)
        
        # Should return the file and all files in the subdirectory
        expected_files = {
            str(self.test_file1),
            str(self.sub_file)
        }
        self.assertEqual(set(result), expected_files)


class TestCliCommands(unittest.TestCase):
    """Test cases for the CLI commands."""

    def setUp(self):
        """Set up test environment."""
        # Create a CLI runner
        self.runner = CliRunner()
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Create test files
        self.test_file = self.test_dir / "test_file.txt"
        with open(self.test_file, "wb") as f:
            f.write(b"Hello, ZenCRC!")
        
        # Calculate the expected CRC32 for the test file
        self.expected_crc = crc32.crc32_from_file(str(self.test_file))

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    @patch('zencrc.crc32.verify_in_filename')
    def test_verify_command(self, mock_verify):
        """Test the verify command."""
        # Set up the mock
        mock_verify.return_value = True
        
        # Run the command using the new subcommand structure
        result = self.runner.invoke(cli, ['verify', str(self.test_file)])
        
        # Check that the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Check that verify_in_filename was called with the correct argument
        mock_verify.assert_called_once_with(str(self.test_file))

    @patch('zencrc.crc32.append_to_filename')
    def test_append_command(self, mock_append):
        """Test the append command."""
        # Set up the mock
        mock_append.return_value = True
        
        # Run the command using the new subcommand structure
        result = self.runner.invoke(cli, ['append', str(self.test_file)])
        
        # Check that the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Check that append_to_filename was called with the correct argument
        mock_append.assert_called_once_with(str(self.test_file))

    @patch('zencrc.crc32.create_sfv_file')
    def test_create_sfv_command(self, mock_create_sfv):
        """Test the create SFV command."""
        # Set up the mock
        mock_create_sfv.return_value = 1
        
        # Create SFV file path
        sfv_file = self.test_dir / "test.sfv"
        
        # Run the command using the new subcommand structure
        result = self.runner.invoke(cli, ['sfv', '-c', str(sfv_file), str(self.test_file)])
        
        # Check that the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Check that create_sfv_file was called with the correct arguments
        mock_create_sfv.assert_called_once_with(str(sfv_file), [str(self.test_file)])

    @patch('zencrc.crc32.verify_sfv_file')
    def test_check_sfv_command(self, mock_verify_sfv):
        """Test the check SFV command."""
        # Set up the mock
        mock_verify_sfv.return_value = {'total': 1, 'ok': 1, 'corrupt': 0, 'not_found': 0}
        
        # Create SFV file path
        sfv_file = self.test_dir / "test.sfv"
        with open(sfv_file, "w") as f:
            f.write(f"{self.test_file} {self.expected_crc}\n")
        
        # Run the command using the new subcommand structure
        result = self.runner.invoke(cli, ['sfv', '-v', str(sfv_file)])
        
        # Check that the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Check that verify_sfv_file was called with the correct argument
        mock_verify_sfv.assert_called_once_with(str(sfv_file))

    @patch('zencrc.zencrc_cli.expand_dirs')
    def test_recurse_option(self, mock_expand_dirs):
        """Test the recurse option."""
        # Set up the mock
        expanded_files = [str(self.test_file)]
        mock_expand_dirs.return_value = expanded_files
        
        # Mock verify_in_filename to avoid actual verification
        with patch('zencrc.crc32.verify_in_filename') as mock_verify:
            mock_verify.return_value = True
            
            # Run the command with recurse option using the new subcommand structure
            result = self.runner.invoke(cli, ['verify', '-r', str(self.test_dir)])
            
            # Check that the command ran successfully
            self.assertEqual(result.exit_code, 0)
            
            # Check that expand_dirs was called with the correct argument
            mock_expand_dirs.assert_called_once_with([str(self.test_dir)])
            
            # Check that verify_in_filename was called with the expanded file
            mock_verify.assert_called_once_with(expanded_files[0])

    def test_multiple_options(self):
        """Test using multiple options together."""
        # Mock all the relevant functions
        with patch('zencrc.crc32.verify_in_filename') as mock_verify, \
             patch('zencrc.crc32.append_to_filename') as mock_append:
            
            mock_verify.return_value = True
            mock_append.return_value = True
            
            # Test multiple operations by running commands sequentially
            verify_result = self.runner.invoke(cli, ['verify', str(self.test_file)])
            append_result = self.runner.invoke(cli, ['append', str(self.test_file)])
            
            # Check that both commands ran successfully
            self.assertEqual(verify_result.exit_code, 0)
            self.assertEqual(append_result.exit_code, 0)
            
            # Check that both functions were called with the correct argument
            mock_verify.assert_called_once_with(str(self.test_file))
            mock_append.assert_called_once_with(str(self.test_file))


if __name__ == "__main__":
    unittest.main()
