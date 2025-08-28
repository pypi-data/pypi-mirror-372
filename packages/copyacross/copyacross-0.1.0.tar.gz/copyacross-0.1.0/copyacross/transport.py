# -----------------------------------------------------------------------------
# CopyAcross - File verification utility
# Copyright (c) 2025 osc@compilersutra.com <osc@compilersutra.com>
#
# Licensed under the MIT License. You may not use this file except in 
# compliance with the License. You may obtain a copy of the License at
# https://opensource.org/licenses/MIT
# -----------------------------------------------------------------------------

import os
from pathlib import Path
import shutil
import paramiko
import getpass
import stat
import sys
import traceback
from .logger import logger
from .exceptions import FileCopyError

class Transport:
    """
    Handles local and remote (SSH/SFTP) file transfers with detailed logging.

    Features:
        - Local copy and folder copy
        - Remote copy and folder copy via SSH/SFTP
        - Logging of operations and exceptions
        - Automatic password prompt caching
    """    
    
    _password_cache = {}

    def __init__(self, ssh_key=None, log_config=False):
        self.ssh_key = ssh_key
        self.log_config = log_config

    # ---------------- Logger with traceback ----------------
    def _log(self, msg):
        if self.log_config:
            logger.info(msg)

    def _log_exception(self, exc: Exception):
        if self.log_config:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = exc_tb.tb_frame.f_code.co_filename
            lineno = exc_tb.tb_lineno
            logger.error(f"Exception in {fname}:{lineno} - {type(exc).__name__}: {exc}")

    # ---------------- Local Copies ----------------
    def copy_local(self, src: Path, dst: Path):
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            self._log(f"Local Copy: {src} -> {dst}")
        except Exception as e:
            self._log_exception(e)
            raise FileCopyError(f"Failed local copy: {src} -> {dst}, {e}")

    def copy_local_folder(self, src: Path, dst: Path):
        try:
            for root, _, files in os.walk(src):
                rel_path = Path(root).relative_to(src)
                target_root = dst / rel_path
                target_root.mkdir(parents=True, exist_ok=True)
                for file in files:
                    local_file = Path(root) / file
                    target_file = target_root / file
                    shutil.copy2(local_file, target_file)
                    self._log(f"Local Folder Copy: {local_file} -> {target_file}")
        except Exception as e:
            self._log_exception(e)
            raise FileCopyError(f"Failed local folder copy: {src} -> {dst}, {e}")

    # ---------------- Remote SSH Client ----------------
    def _get_ssh_client(self, host, user):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.ssh_key:
                key = paramiko.RSAKey.from_private_key_file(self.ssh_key)
                ssh.connect(hostname=host, username=user, pkey=key)
            else:
                host_id = f"{user}@{host}"
                if host_id not in self._password_cache:
                    self._password_cache[host_id] = getpass.getpass(f"Password for {host_id}: ")
                ssh.connect(
                    hostname=host,
                    username=user,
                    password=self._password_cache[host_id],
                    allow_agent=False,
                    look_for_keys=False
                )
            return ssh
        except Exception as e:
            self._log_exception(e)
            raise FileCopyError(f"Failed to connect SSH: {user}@{host}, {e}")

    # ---------------- Remote → Local ----------------
    def fetch_remote(self, host_user: str, remote_path: str, local_path: Path):
        try:
            user, host = host_user.split("@")
            ssh = self._get_ssh_client(host, user)
            sftp = ssh.open_sftp()
            local_path.parent.mkdir(parents=True, exist_ok=True)
            sftp.get(str(remote_path), str(local_path))
            self._log(f"Fetched Remote File: {user}@{host}:{remote_path} -> {local_path}")
            sftp.close()
            ssh.close()
        except Exception as e:
            self._log_exception(e)
            raise FileCopyError(f"Failed fetching remote file: {host_user}:{remote_path} -> {local_path}, {e}")

    def fetch_remote_folder(self, host_user: str, remote_folder, local_folder: Path):
        try:
            user, host = host_user.split("@")
            ssh = self._get_ssh_client(host, user)
            sftp = ssh.open_sftp()
            self._log(f"Fetching Remote Folder: {user}@{host}:{remote_folder} -> {local_folder}")

            def _walk_remote(remote_path):
                files = []
                dirs = []
                for entry in sftp.listdir_attr(remote_path):
                    mode = entry.st_mode
                    name = entry.filename
                    path = f"{remote_path}/{name}"
                    if stat.S_ISDIR(mode):
                        dirs.append(name)
                    else:
                        files.append(name)
                yield remote_path, dirs, files
                for d in dirs:
                    yield from _walk_remote(f"{remote_path}/{d}")

            for root, dirs, files in _walk_remote(str(remote_folder)):
                rel_path = os.path.relpath(root, remote_folder)
                target_root = local_folder / rel_path
                target_root.mkdir(parents=True, exist_ok=True)
                for file in files:
                    remote_file = f"{root}/{file}"
                    local_file = target_root / file
                    sftp.get(remote_file, str(local_file))
                    self._log(f"Fetched Remote File: {user}@{host}:{remote_file} -> {local_file}")

            sftp.close()
            ssh.close()
        except Exception as e:
            self._log_exception(e)
            raise FileCopyError(f"Failed fetching remote folder: {host_user}:{remote_folder} -> {local_folder}, {e}")

    # ---------------- Local → Remote ----------------
    def copy_remote(self, src: Path, dst: str, host: str, user: str):
        try:
            ssh = self._get_ssh_client(host, user)
            sftp = ssh.open_sftp()
            sftp.put(str(src), dst)
            self._log(f"Remote Copy: {src} -> {user}@{host}:{dst}")
            sftp.close()
            ssh.close()
        except Exception as e:
            self._log_exception(e)
            raise FileCopyError(f"Failed remote copy: {src} -> {user}@{host}:{dst}, {e}")

    def copy_remote_folder(self, src: Path, dst: str, host: str, user: str):
        try:
            ssh = self._get_ssh_client(host, user)
            sftp = ssh.open_sftp()
            for root, _, files in os.walk(src):
                rel_path = Path(root).relative_to(src)
                remote_root = Path(dst) / rel_path

                try:
                    sftp.mkdir(str(remote_root))
                except IOError:
                    pass  # Directory exists

                for file in files:
                    local_file = Path(root) / file
                    remote_file = remote_root / file
                    sftp.put(str(local_file), str(remote_file))
                    self._log(f"Remote Folder Copy: {local_file} -> {user}@{host}:{remote_file}")

            sftp.close()
            ssh.close()
        except Exception as e:
            self._log_exception(e)
            raise FileCopyError(f"Failed remote folder copy: {src} -> {user}@{host}:{dst}, {e}")
