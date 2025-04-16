"""
Unit tests for the zencrc.crc32 module.
"""
import os
import tempfile
import unittest
from pathlib import Path

from zencrc import crc32


class TestCRC32Functions(unittest.TestCase):
    """Test cases for the core CRC32 functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Create a test file with known content
        self.test_file_path = self.test_dir / "test_file.txt"
        with open(self.test_file_path, "wb") as f:
            f.write(b"Hello, ZenCRC!")
        
        # Calculate the expected CRC32 for the test file
        # We'll calculate this dynamically to ensure it matches
        self.expected_crc = crc32.crc32_from_file(str(self.test_file_path))
        
        # Create a file with CRC in the filename
        self.file_with_crc = self.test_dir / f"test_file [{self.expected_crc}].txt"
        with open(self.file_with_crc, "wb") as f:
            f.write(b"Hello, ZenCRC!")
        
        # Create a file with incorrect CRC in the filename
        self.file_with_wrong_crc = self.test_dir / "test_file [DEADBEEF].txt"
        with open(self.file_with_wrong_crc, "wb") as f:
            f.write(b"Hello, ZenCRC!")

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_crc32_from_file(self):
        """Test CRC32 calculation from a file."""
        result = crc32.crc32_from_file(str(self.test_file_path))
        self.assertEqual(result, self.expected_crc)

    def test_get_filename_display(self):
        """Test filename display formatting."""
        # Test normal filename
        result = crc32.get_filename_display(str(self.test_file_path))
        self.assertEqual(result, "test_file.txt")
        
        # Test long filename truncation
        long_name = "a" * 100 + ".txt"
        long_path = self.test_dir / long_name
        result = crc32.get_filename_display(str(long_path))
        self.assertEqual(len(result), 47)  # 44 chars + 3 dots
        self.assertTrue(result.endswith("..."))

    def test_extract_crc_from_filename(self):
        """Test extracting CRC32 from filename."""
        # Test file with CRC
        result = crc32.extract_crc_from_filename(str(self.file_with_crc))
        self.assertEqual(result, self.expected_crc)
        
        # Test file without CRC
        result = crc32.extract_crc_from_filename(str(self.test_file_path))
        self.assertIsNone(result)
        
        # Test file with CRC in parentheses
        file_with_parens = self.test_dir / f"test_file ({self.expected_crc}).txt"
        with open(file_with_parens, "wb") as f:
            f.write(b"Hello, ZenCRC!")
        result = crc32.extract_crc_from_filename(str(file_with_parens))
        self.assertEqual(result, self.expected_crc)

    def test_verify_in_filename(self):
        """Test verifying CRC32 in filename."""
        # Test file with correct CRC
        result = crc32.verify_in_filename(str(self.file_with_crc))
        self.assertTrue(result)
        
        # Test file with incorrect CRC
        result = crc32.verify_in_filename(str(self.file_with_wrong_crc))
        self.assertFalse(result)
        
        # Test file without CRC
        result = crc32.verify_in_filename(str(self.test_file_path))
        self.assertFalse(result)

    def test_append_to_filename(self):
        """Test appending CRC32 to filename."""
        # Test appending to a file without CRC
        result = crc32.append_to_filename(str(self.test_file_path))
        self.assertTrue(result)
        
        # Verify the file was renamed correctly
        expected_path = self.test_dir / f"test_file [{self.expected_crc}].txt"
        self.assertTrue(expected_path.exists())
        
        # Test appending to a file that already has CRC
        result = crc32.append_to_filename(str(expected_path))
        self.assertFalse(result)  # Should return False for already having CRC

    def test_format_file_size(self):
        """Test file size formatting."""
        # Test bytes
        self.assertEqual(crc32.format_file_size(500), "500 B")
        
        # Test kilobytes
        self.assertEqual(crc32.format_file_size(1500), "1.5 KB")
        
        # Test megabytes
        self.assertEqual(crc32.format_file_size(1500000), "1.4 MB")
        
        # Test gigabytes
        self.assertEqual(crc32.format_file_size(1500000000), "1.4 GB")


class TestSFVFunctions(unittest.TestCase):
    """Test cases for SFV file functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Create test files
        self.test_file1 = self.test_dir / "file1.txt"
        with open(self.test_file1, "wb") as f:
            f.write(b"File 1 content")
        
        self.test_file2 = self.test_dir / "file2.txt"
        with open(self.test_file2, "wb") as f:
            f.write(b"File 2 content")
        
        # Calculate CRCs
        self.crc1 = crc32.crc32_from_file(str(self.test_file1))
        self.crc2 = crc32.crc32_from_file(str(self.test_file2))
        
        # Create SFV file
        self.sfv_file = self.test_dir / "test.sfv"
        with open(self.sfv_file, "w") as f:
            f.write("; Test SFV file\n")
            f.write(f"{self.test_file1} {self.crc1}\n")
            f.write(f"{self.test_file2} {self.crc2}\n")
        
        # Create SFV file with incorrect CRC
        self.bad_sfv_file = self.test_dir / "bad.sfv"
        with open(self.bad_sfv_file, "w") as f:
            f.write("; Test SFV file with bad CRC\n")
            f.write(f"{self.test_file1} {self.crc1}\n")
            f.write(f"{self.test_file2} DEADBEEF\n")  # Incorrect CRC

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_parse_sfv_line(self):
        """Test parsing SFV file lines."""
        # Test valid line
        result = crc32.parse_sfv_line(f"{self.test_file1} {self.crc1}")
        self.assertEqual(result, (str(self.test_file1), self.crc1))
        
        # Test comment line
        result = crc32.parse_sfv_line("; This is a comment")
        self.assertIsNone(result)
        
        # Test empty line
        result = crc32.parse_sfv_line("")
        self.assertIsNone(result)
        
        # Test invalid line (no space)
        result = crc32.parse_sfv_line("invalidline")
        self.assertIsNone(result)
        
        # Test invalid CRC format
        result = crc32.parse_sfv_line(f"{self.test_file1} XYZ")
        self.assertIsNone(result)

    def test_verify_sfv_file(self):
        """Test verifying SFV files."""
        # Test valid SFV file
        result = crc32.verify_sfv_file(str(self.sfv_file))
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["ok"], 2)
        self.assertEqual(result["corrupt"], 0)
        
        # Test SFV file with incorrect CRC
        result = crc32.verify_sfv_file(str(self.bad_sfv_file))
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["ok"], 1)
        self.assertEqual(result["corrupt"], 1)
        
        # Test SFV file with missing file
        missing_file = self.test_dir / "missing.sfv"
        with open(missing_file, "w") as f:
            f.write(f"{self.test_dir}/nonexistent.txt {self.crc1}\n")
        result = crc32.verify_sfv_file(str(missing_file))
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["not_found"], 1)

    def test_create_sfv_file(self):
        """Test creating SFV files."""
        # Create a new SFV file
        new_sfv = self.test_dir / "new.sfv"
        files = [str(self.test_file1), str(self.test_file2)]
        result = crc32.create_sfv_file(str(new_sfv), files)
        
        # Check result
        self.assertEqual(result, 2)  # 2 files added
        self.assertTrue(new_sfv.exists())
        
        # Verify content
        with open(new_sfv, "r") as f:
            content = f.read()
            self.assertIn(f"{self.test_file1} {self.crc1}", content)
            self.assertIn(f"{self.test_file2} {self.crc2}", content)
        
        # Test with directory in file list
        files_with_dir = [str(self.test_file1), str(self.test_dir)]
        result = crc32.create_sfv_file(str(self.test_dir / "with_dir.sfv"), files_with_dir)
        self.assertEqual(result, 1)  # Only 1 file should be added


if __name__ == "__main__":
    unittest.main()
