# -----------------------------------------------------------------------------
# CopyAcross - Cross-platform bi-directional file sync tool
# Copyright (c) 2025 osc@compilersutra.com <osc@compilersutra.com>
#
# Licensed under the MIT License. You may not use this file except in 
# compliance with the License. You may obtain a copy of the License at
# https://opensource.org/licenses/MIT
# -----------------------------------------------------------------------------

import yaml
import os
from pathlib import Path
from .logger import logger
from .exceptions import FileCopyError

class ConfigLoader:
    """Load and validate configuration from a YAML file."""

    @staticmethod
    def load_config(config_path: str) -> dict:
        """
        Load YAML configuration and validate mandatory fields.

        Args:
            config_path (str): Path to the YAML configuration file.

        Returns:
            dict: Parsed configuration.

        Raises:
            FileCopyError: If file is missing, malformed, or mandatory fields are absent.
        """
        if not os.path.exists(config_path):
            raise FileCopyError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise FileCopyError(f"Failed to parse config: {e}")

        # Validate mandatory fields
        if "sources" not in config or "destinations" not in config:
            raise FileCopyError("Config must include 'sources' and 'destinations'.")

        # Log config load
        logger.info(f"Configuration loaded from {config_path}")
        return config
