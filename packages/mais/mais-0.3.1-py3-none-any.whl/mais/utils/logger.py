import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.WARNING,  # Default to WARNING level for less verbosity
    format='MAIS [%(levelname)s]: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger('mais')
