import logging
import os
from datetime import datetime
from pathlib import Path


class Logger:
    def __init__(self, log_dir='logs'):
        # Criar diretório de logs se não existir
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        # Nome do arquivo de log com data
        log_filename = f"{log_dir}/bot-{datetime.now().strftime('%Y-%m-%d')}.log"

        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

    def success(self, message):
        self.logger.info(f"✅ {message}")

    def debug(self, message):
        self.logger.debug(message)
