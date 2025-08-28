# -----------------------------------------------------------------------------
# CopyAcross - Cross-platform bi-directional file sync tool
# Copyright (c) 2025 osc@compilersutra.com <osc@compilersutra.com>
#
# Licensed under the MIT License. You may not use this file except in 
# compliance with the License. You may obtain a copy of the License at
# https://opensource.org/licenses/MIT
# -----------------------------------------------------------------------------

import click
from pathlib import Path
from .config import ConfigLoader
from .sync_engine import SyncEngine
from .logger import setup_logger, logger
from .exceptions import FileCopyError

# ---------------- Initialize Logging ----------------
# Logs will include timestamps, levels, filenames, and line numbers
setup_logger()

@click.command()
@click.option("--config", default="config.yaml", help="Path to YAML config file")
def main(config):
    """
    Cross-platform bi-directional sync tool.

    Example usage:
      python -m copyacross --config my_config.yaml
    """
    try:
        # ---------------- Load Config ----------------
        cfg = ConfigLoader.load_config(config)

        # ---------------- Initialize Sync Engine ----------------
        sync_tool = SyncEngine(cfg)

        # ---------------- Run Sync ----------------
        if cfg.get("sync_direction", "both") == "one-way":
            sync_tool.sync_one_way()
        else:
            sync_tool.sync_both_ways()

        print("Sync completed successfully!")

    except FileCopyError as e:
        logger.error(f"[FILE COPY ERROR] {e}")
        print(f"[ERROR] {e}")
    except FileNotFoundError as e:
        logger.error(f"[CONFIG/FILE NOT FOUND] {e}")
        print(f"[ERROR] {e}")
    except Exception as e:
        # Catch-all for unexpected errors
        import traceback
        logger.error(f"[UNEXPECTED ERROR] {e}\n{traceback.format_exc()}")
        print(f"[UNEXPECTED ERROR] {e}")

if __name__ == "__main__":
    main()
