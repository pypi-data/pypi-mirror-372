# -----------------------------------------------------------------------------
# CopyAcross - SyncEngine for cross-platform file synchronization
# Copyright (c) 2025 osc@compilersutra.com <osc@compilersutra.com>
#
# Licensed under the MIT License. You may not use this file except in 
# compliance with the License. You may obtain a copy of the License at
# https://opensource.org/licenses/MIT
# -----------------------------------------------------------------------------


import os
import tempfile
from pathlib import Path, PurePosixPath
from concurrent.futures import ThreadPoolExecutor, as_completed
from .transport import Transport
from .verifier import FileVerifier
from .logger import logger
from .exceptions import FileCopyError
import sys
import traceback


class SyncEngine:
    """
    Performs uni- and bi-directional sync between sources and destinations.

    Features:
        - Local ↔ Local, Local ↔ Remote, Remote ↔ Local, Remote ↔ Remote
        - Folder recursion and file verification
        - Parallel transfers using ThreadPoolExecutor
        - Configurable logging
        - Dry-run mode placeholder (future enhancement)
    
    Args:
        config (dict): Configuration dictionary from YAML file.
    """
    def __init__(self, config):
        self.verify = config.get("verify", True)
        self.parallel = config.get("parallel", 4)
        self.log_config = config.get("log_config", False)
        self.transport = Transport(ssh_key=config.get("ssh_key"), log_config=self.log_config)

        sources = config["sources"]
        destinations = config["destinations"]

        # Reverse logic
        if config.get("reverse", False):
            self.sources = [{"path": dst["path"], "type": dst.get("type", "folder"), "host": dst.get("host")}
                            for dst in destinations]
            self.destinations = [{"path": src["path"], "type": src.get("type", "folder"), "host": None}
                                 for src in sources]
        else:
            self.sources = sources
            self.destinations = destinations

        # Log configuration
        if self.log_config:
            logger.info("Configured Sources:")
            for s in self.sources:
                logger.info(f"  {s}")
            logger.info("Configured Destinations:")
            for d in self.destinations:
                logger.info(f"  {d}")

    # ---------------- Exception Logging ----------------
    def _log_exception(self, exc: Exception):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        if exc_tb:
            fname = exc_tb.tb_frame.f_code.co_filename
            lineno = exc_tb.tb_lineno
        else:
            fname = "<unknown>"
            lineno = 0
        logger.error(f"Exception in {fname}:{lineno} - {type(exc).__name__}: {exc}")

    # ---------------- Verification Helper ----------------
    def _verify(self, src_file: Path, dst_file: Path):
        if not dst_file.exists():
            logger.warning(f"Destination file missing, skipping verification: {dst_file}")
            return
        if not FileVerifier.verify(src_file, dst_file):
            raise FileCopyError(f"Verification failed: {src_file} -> {dst_file}")

    # ---------------- Sync Single File/Folder ----------------
    def _sync_file(self, src, dst):
        src_path = Path(src["path"])
        dst_path = dst["path"]
        src_host = src.get("host")
        dst_host = dst.get("host")
        dst_user, dst_hostname = (dst_host.split("@") if dst_host else (None, None))

        action_desc = f"{src_path} ({'remote' if src_host else 'local'}) -> " \
                      f"{dst_path} ({'remote' if dst_host else 'local'})"
        if self.log_config:
            logger.info(f"Syncing: {action_desc}")

        try:
            # ---------------- Local -> Local ----------------
            if not src_host and not dst_host:
                if src.get("type") == "folder":
                    self.transport.copy_local_folder(src_path, Path(dst_path))
                else:
                    self.transport.copy_local(src_path, Path(dst_path))

            # ---------------- Local -> Remote ----------------
            elif not src_host and dst_host:
                if src.get("type") == "folder":
                    self.transport.copy_remote_folder(src_path, dst_path, dst_hostname, dst_user)
                else:
                    self.transport.copy_remote(src_path, dst_path, dst_hostname, dst_user)

            # ---------------- Remote -> Local ----------------
            elif src_host and not dst_host:
                if src.get("type") == "folder":
                    self.transport.fetch_remote_folder(src_host, str(src_path), Path(dst_path))
                else:
                    self.transport.fetch_remote(src_host, str(src_path), Path(dst_path))

            # ---------------- Remote -> Remote ----------------
            else:
                if self.log_config:
                    logger.info("Remote -> Remote detected, using temporary local copy")
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmp_path = Path(tmpdir) / src_path.name
                    if src.get("type") == "folder":
                        self.transport.fetch_remote_folder(src_host, str(src_path), tmp_path)
                    else:
                        self.transport.fetch_remote(src_host, str(src_path), tmp_path)

                    if src.get("type") == "folder":
                        self.transport.copy_remote_folder(tmp_path, dst_path, dst_hostname, dst_user)
                    else:
                        self.transport.copy_remote(tmp_path, dst_path, dst_hostname, dst_user)
                    if self.log_config:
                        logger.info(f"Remote -> Remote completed via temp dir: {tmp_path}")

            # ---------------- Verification ----------------
            if self.verify:
                if src.get("type") == "folder":
                    for root, _, files in os.walk(src_path):
                        for file in files:
                            src_file = Path(root) / file
                            rel_path = src_file.relative_to(src_path)
                            dst_file = Path(dst_path) / rel_path
                            self._verify(src_file, dst_file)
                else:
                    self._verify(src_path, Path(dst_path))

            if self.log_config:
                logger.info(f"Completed: {action_desc}")

        except Exception as e:
            if self.log_config:
                self._log_exception(e)
            raise

    # ---------------- One-way Sync ----------------
    def sync_one_way(self):
        if self.log_config:
            logger.info(f"=== Starting One-Way Sync ({len(self.sources)} source(s) x {len(self.destinations)} dest(s)) ===")

        futures = []
        with ThreadPoolExecutor(max_workers=self.parallel) as executor:
            for src in self.sources:
                for dst in self.destinations:
                    futures.append(executor.submit(self._sync_file, src, dst))

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    if self.log_config:
                        self._log_exception(e)

        if self.log_config:
            logger.info("=== One-Way Sync Completed ===")

    # ---------------- Bi-directional Sync ----------------
    def sync_both_ways(self):
        if self.log_config:
            logger.info("=== Starting Source -> Destination Sync ===")
        self.sync_one_way()

        if self.log_config:
            logger.info("=== Starting Destination -> Source Sync ===")
        self.sources, self.destinations = self.destinations, self.sources
        self.sync_one_way()
