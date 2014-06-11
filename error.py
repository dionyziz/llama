# ----------------------------------------------------------------------
# error.py
#
# Simple error logger for the llama compiler. Provides methods for
# logging and reporting errors of varying severities.
# Utilizes python logging.
#
# Author: Nick Korasidis <Renelvon@gmail.com>
# ----------------------------------------------------------------------

import logging

# On import, creates a logger if one isn't already available
llama_logger = logging.getLogger('llama') 

# Add some debug info to the logger.
debug = llama_logger.debug

# Add an error to the logger."""
error = llama_logger.error

# Add some general info to the logger."""
info = llama_logger.info

# Add a warning to the logger."""
warning = llama_logger.warning
