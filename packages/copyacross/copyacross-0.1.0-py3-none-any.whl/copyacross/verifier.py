# -----------------------------------------------------------------------------
# CopyAcross - File verification utility
# Copyright (c) 2025 osc@compilersutra.com <osc@compilersutra.com>
#
# Licensed under the MIT License. You may not use this file except in 
# compliance with the License. You may obtain a copy of the License at
# https://opensource.org/licenses/MIT
# -----------------------------------------------------------------------------

import hashlib
from pathlib import Path
from .logger import logger

class FileVerifier:
    """Compute and verify file hashes using SHA-256."""

    @staticmethod
    def sha256(file_path: str) -> str:
        """
        Compute SHA-256 hash of a file.

        Args:
            file_path (str): Path to the file.

        Returns:
            str: Hexadecimal SHA-256 hash.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found for hashing: {file_path}")
        
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def verify(source_path: str, dest_path: str, skip_missing: bool = False) -> bool:
        """
        Verify that two files have identical SHA-256 hashes.

        Args:
            source_path (str): Path to source file.
            dest_path (str): Path to destination file.
            skip_missing (bool): If True, skip verification if destination is missing.

        Returns:
            bool: True if files match, False otherwise.

        Logs:
            Provides info about verification success or warnings if skipped/mismatched.
        """
        source_path = Path(source_path)
        dest_path = Path(dest_path)

        if not source_path.exists():
            logger.error(f"Source file missing: {source_path}")
            return False

        if not dest_path.exists():
            if skip_missing:
                logger.warning(f"Destination file missing, skipping verification: {dest_path}")
                return True
            else:
                logger.error(f"Destination file missing: {dest_path}")
                return False

        try:
            source_hash = FileVerifier.sha256(source_path)
            dest_hash = FileVerifier.sha256(dest_path)
            if source_hash == dest_hash:
                logger.info(f"Verified: {source_path} -> {dest_path}")
                return True
            else:
                logger.error(f"Hash mismatch: {source_path} -> {dest_path}")
                return False
        except Exception as e:
            import traceback
            logger.error(f"Verification failed for {source_path} -> {dest_path}: {e}\n{traceback.format_exc()}")
            return False
