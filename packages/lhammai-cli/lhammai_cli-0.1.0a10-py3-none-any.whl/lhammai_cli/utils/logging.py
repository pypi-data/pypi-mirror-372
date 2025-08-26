from loguru import logger

from lhammai_cli.settings import settings

logger.remove()
logger.add(settings.log_file, level=settings.log_level, retention=settings.log_retention)
