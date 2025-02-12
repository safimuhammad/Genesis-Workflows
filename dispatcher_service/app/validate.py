#!/usr/bin/env python
import os
import glob

def validate_output_files():
    # Get the path to the output directory
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    
    # Count all .md files in the output directory
    md_files = glob.glob(os.path.join(output_dir, "*.md"))
    file_count = len(md_files)
    
    # Check if the count matches expected number
    expected_count = 500
    if file_count == expected_count:
        print(f"Test PASSED: Found expected {file_count} files")
        return True
    else:
        print(f"Test FAILED: Found {file_count} files, expected {expected_count}")
        return False

if __name__ == "__main__":
    validate_output_files() 