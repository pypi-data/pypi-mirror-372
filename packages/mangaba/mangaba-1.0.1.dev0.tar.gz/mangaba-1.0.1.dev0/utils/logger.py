from loguru import logger
import sys
from config import config

def get_logger(name: str = "MangabaAI"):
    """Logger simples e bonito."""
    
    # Remove handlers padrão
    logger.remove()
    
    # Adiciona handler colorido para console
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[name]}</cyan> | <level>{message}</level>",
        level=config.log_level,
        colorize=True
    )
    
    return logger.bind(name=name)