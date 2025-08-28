# -----------------------------------------------------------------------------
# CopyAcross - SyncEngine for cross-platform file synchronization
# Copyright (c) 2025 osc@compilersutra.com <osc@compilersutra.com>
#
# Licensed under the MIT License. You may not use this file except in 
# compliance with the License. You may obtain a copy of the License at
# https://opensource.org/licenses/MIT
# -----------------------------------------------------------------------------

import logging

logger = logging.getLogger("copyacross")

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
