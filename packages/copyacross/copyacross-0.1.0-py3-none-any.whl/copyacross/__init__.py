# -----------------------------------------------------------------------------
# CopyAcross - Cross-platform bi-directional file sync tool
# Copyright (c) 2025 osc@compilersutra.com <osc@compilersutra.com>
#
# Licensed under the MIT License. You may not use this file except in 
# compliance with the License. You may obtain a copy of the License at
# https://opensource.org/licenses/MIT
# -----------------------------------------------------------------------------

"""
CopyAcross Python API

Provides a simple function `sync()` for running the file sync engine
directly from Python scripts, without using the CLI.

Example usage:
    # Newbie style
    import copyacross
    copyacross.sync("config.yaml")

    # Expert style
    import copyacross
    copyacross.sync(
        "config.yaml",
        log_file="sync.log",
        log_config=True,
        dry_run=True
    )
"""

from pathlib import Path
import yaml
import logging
from .sync_engine import SyncEngine
import copyacross.logger as logger_module

# dr
def sync(config_path: str, log_file: str = None, log_config: bool = None, dry_run: bool = False):
    """
    Run CopyAcross using a YAML config file.

    Args:
        config_path (str): Path to YAML configuration.
        log_file (str, optional): Placeholder for future log file support.
        log_config (bool, optional): Placeholder for future log configuration override.
        dry_run (bool, optional): Placeholder for future dry-run implementation.

    Note:
        Currently, log_file, log_config, and dry_run are not fully implemented.
        They exist as placeholders for future functionality.
    """
    
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Load YAML config
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    # Override log_config if provided
    if log_config is not None:
        config["log_config"] = log_config
    else:
        config["log_config"] = bool(config.get("log_config", False))

    # Setup logger
    logger = logger_module.logger

    # Remove any existing handlers
    if logger.handlers:
        for h in logger.handlers[:]:
            logger.removeHandler(h)

    # Add new handler
    handler = logging.FileHandler(log_file) if log_file else logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Inject dry_run flag into config for SyncEngine
    config["dry_run"] = dry_run

    # Initialize SyncEngine
    engine = SyncEngine(config)

    # Run sync based on direction
    if config.get("sync_direction", "one-way") == "both":
        engine.sync_both_ways()
    else:
        engine.sync_one_way()

    if dry_run:
        logger.info("Dry-run mode enabled: no files were actually copied.")
