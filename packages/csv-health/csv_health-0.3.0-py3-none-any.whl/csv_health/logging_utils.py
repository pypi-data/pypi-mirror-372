import logging
import os
import warnings
from logging.handlers import RotatingFileHandler
from pathlib import Path


_CFG_FLAG = "_csv_health_root_configured"


def _configure_root_logger(log_dir: Path) -> logging.Logger:
    """
    Конфигурирует родительский логгер "csv_health":
    - консоль + ротация файла <home>/logs/app.log
    - уровень из CSV_HEALTH_LOGLEVEL (по умолчанию INFO)
    - warnings → в логгер, без красноты в консоли
    """
    level_name = os.environ.get("CSV_HEALTH_LOGLEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    root = logging.getLogger("csv_health")
    if getattr(root, _CFG_FLAG, False):
        return root

    root.setLevel(level)
    root.propagate = False  # не пускаем дальше в root logger, чтобы избежать дубликатов
    log_dir.mkdir(parents=True, exist_ok=True)

    # --- консоль ---
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    root.addHandler(ch)

    # --- файл (ротация) ---
    fh = RotatingFileHandler(log_dir / "app.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root.addHandler(fh)

    # --- warnings → в логгер, без «красного» в IDE ---
    def _showwarning(message, category, filename, lineno, file=None, line=None):
        root.warning("%s:%s: %s: %s", filename, lineno, category.__name__, message)

    warnings.showwarning = _showwarning
    warnings.simplefilter("ignore")  # глобально приглушаем (но всё равно попадут к нам через showwarning при желании)

    setattr(root, _CFG_FLAG, True)
    return root


def setup_logger(name: str, log_dir: Path) -> logging.Logger:
    """
    Возвращает модульный логгер (например, 'csv_health.api').
    Внутри гарантирует, что корневой 'csv_health' настроен один раз.
    """
    _configure_root_logger(log_dir)
    logger = logging.getLogger(name)
    # дочерние логгеры без своих хендлеров → пишут через родителя 'csv_health'
    logger.propagate = True
    return logger
