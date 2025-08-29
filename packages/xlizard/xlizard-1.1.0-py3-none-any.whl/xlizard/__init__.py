__version__ = "1.0.12"  # Должно совпадать с версией в setup.py
version = "1.0.12"      # Для обратной совместимости

# Явно экспортируем нужные модули
from .xlizard import *
from xlizard.combined_metrics import CombinedMetrics
from xlizard.sourcemonitor_metrics import SourceMonitorMetrics

__all__ = ['CombinedMetrics', 'load_thresholds', 'DEFAULT_THRESHOLDS', 'Config', 'SourceMonitorMetrics']