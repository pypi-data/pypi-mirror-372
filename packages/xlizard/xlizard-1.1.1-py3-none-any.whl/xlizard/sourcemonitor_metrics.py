import os
import sys
import logging
import re
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET
from tqdm import tqdm
from collections import defaultdict
from typing import Dict, List, Optional, DefaultDict

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

class Config:
    """Конфигурация анализатора"""
    EXCLUDE_DIRS = {'.git', 'venv', '__pycache__', 'include'}
    SUPPORTED_EXTENSIONS = {'.c', '.h'}
    METRICS = [
        'comment_percentage',
        'max_block_depth',
        'pointer_operations',
        'preprocessor_directives'
    ]
    THRESHOLDS = {
        'comment_percentage': 20,
        'max_block_depth': 5,
        'pointer_operations': 20,
        'preprocessor_directives': 15
    }

class FileAnalyzer:
    """Анализатор отдельных файлов"""
    @staticmethod
    def _remove_string_literals(content: str) -> str:
        """Удаляет строковые литералы для упрощения анализа"""
        return re.sub(r'"[^"]*"', '', content)

    @staticmethod
    def _count_comments(content: str) -> int:
        """Подсчёт количества строк с комментариями"""
        lines = content.split('\n')
        comment_lines = 0
        in_block_comment = False
        
        for line in lines:
            line = line.strip()
            if in_block_comment:
                comment_lines += 1
                if '*/' in line:
                    in_block_comment = False
                continue
            if line.startswith('/*'):
                comment_lines += 1
                in_block_comment = True
                if '*/' in line:
                    in_block_comment = False
            elif line.startswith('//'):
                comment_lines += 1
                
        return comment_lines

    @staticmethod
    def _calculate_block_depth(content: str, is_function: bool = False) -> int:
        """Вычисление максимальной глубины вложенности для файла или функции"""
        max_depth = 0
        current_depth = 0
        in_function = not is_function  # Для анализа функции начинаем сразу с глубины 0
        
        # Удаляем комментарии и строковые литералы для корректного анализа
        content_clean = FileAnalyzer._remove_comments_and_strings(content)
        
        for char in content_clean:
            if char == '{':
                current_depth += 1
                if in_function:
                    max_depth = max(max_depth, current_depth)
            elif char == '}':
                if in_function:
                    current_depth -= 1
                if current_depth == 0:
                    in_function = not is_function  # Выходим из функции
                    
        return max_depth
    
    @staticmethod
    def _remove_comments_and_strings(content: str) -> str:
        """Удаляет комментарии и строковые литералы, корректно обрабатывая кодировки"""
        # Сначала пробуем декодировать если это bytes
        if isinstance(content, bytes):
            try:
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    content = content.decode('cp1251')  # Windows-1251
                except UnicodeDecodeError:
                    content = content.decode('latin-1')  # Fallback
        
        # Удаляем блочные комментарии /* */
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Удаляем однострочные комментарии //
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        
        # Удаляем строковые литералы
        content = re.sub(r'"[^"]*"', '', content)
        content = re.sub(r"'[^']*'", '', content)
        
        # Удаляем препроцессорные директивы
        content = re.sub(r'^#.*?$', '', content, flags=re.MULTILINE)
        
        return content
    
    @classmethod
    def analyze(cls, file_path: str) -> Optional[Dict[str, float]]:
        """Анализ файла и возврат метрик с поддержкой разных кодировок"""
        try:
            # Пробуем разные кодировки
            encodings = ['utf-8', 'cp1251', 'latin-1', 'iso-8859-1']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                # Если все кодировки не подошли, читаем как бинарный и пробуем декодировать
                with open(file_path, 'rb') as f:
                    binary_content = f.read()
                    content = binary_content.decode('utf-8', errors='ignore')
            
            content_no_strings = FileAnalyzer._remove_comments_and_strings(content)
            total_lines = len(content.split('\n'))
            comment_lines = cls._count_comments(content)
            
            return {
                'file_name': os.path.basename(file_path),
                'file_path': os.path.relpath(file_path),
                'comment_percentage': (comment_lines / total_lines * 100) if total_lines else 0,
                'max_block_depth': FileAnalyzer._calculate_block_depth(content_no_strings),
                'pointer_operations': content_no_strings.count('*') + content_no_strings.count('&'),
                'preprocessor_directives': len([l for l in content.split('\n') if l.strip().startswith('#')]),
            }
        except Exception as e:
            logger.warning(f"Ошибка анализа {file_path}: {str(e)}")
            return None

class MetricsAggregator:
    """Агрегация метрик по всем файлам"""
    def __init__(self):
        self.file_metrics: List[Dict[str, float]] = []
        self.total_metrics: DefaultDict[str, float] = defaultdict(float)
        self.counts: DefaultDict[str, int] = defaultdict(int)

    def add_file_metrics(self, metrics: Dict[str, float]) -> None:
        """Добавление метрик файла"""
        self.file_metrics.append(metrics)
        for key in Config.METRICS:
            if key in metrics:
                self.total_metrics[key] += metrics[key]
                self.counts[key] += 1

    def get_averages(self) -> Dict[str, float]:
        """Расчёт средних значений"""
        return {
            metric: self.total_metrics[metric] / self.counts[metric]
            for metric in Config.METRICS
            if self.counts[metric] > 0
        }

class ReportGenerator:
    """Генерация отчётов"""
    @staticmethod
    def generate_xml(metrics: List[Dict[str, float]], output_path: str) -> None:
        """Генерация XML отчёта"""
        # Создаем папку output если ее нет
        output_dir = os.path.dirname(output_path)
        try:
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Папка {output_dir} успешно создана или уже существует")
        except OSError as e:
            logger.error(f"Не удалось создать папку {output_dir}: {str(e)}")
            raise

        root = ET.Element('sourcemonitor_metrics')
        for file_metrics in metrics:
            file_node = ET.SubElement(root, 'file', 
                                   name=file_metrics['file_name'],
                                   path=file_metrics['file_path'])
            for metric in Config.METRICS:
                ET.SubElement(file_node, metric).text = str(file_metrics.get(metric, 0))
        
        tree = ET.ElementTree(root)
        try:
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            logger.info(f"XML-отчёт успешно сохранён в {output_path}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении отчёта в {output_path}: {str(e)}")
            raise

class SourceMonitorMetrics:
    """Основной класс анализатора"""
    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        # Правильное определение корня пакета xlizard
        package_root = self._find_package_root()
        self.output_xml = os.path.join(package_root, 'output', 'sourcemonitor_metrics.xml')
        self.aggregator = MetricsAggregator()
        logger.info(f"Отчёт будет сохранён в: {self.output_xml}")

    def _find_package_root(self) -> str:
        """Находит корень пакета xlizard"""
        # Ищем папку с именем 'xlizard' в пути текущего файла
        current_dir = os.path.dirname(os.path.abspath(__file__))
        while current_dir != os.path.dirname(current_dir):  # Пока не дойдем до корня файловой системы
            if os.path.basename(current_dir) == 'xlizard':
                return current_dir
            current_dir = os.path.dirname(current_dir)
        # Если не нашли, используем текущую директорию
        logger.warning("Не удалось найти корень пакета xlizard, используется текущая директория")
        return os.getcwd()

    def _collect_files(self) -> List[str]:
        """Сбор файлов для анализа"""
        c_files = []
        for root, dirs, files in os.walk(self.path):
            dirs[:] = [d for d in dirs if d not in Config.EXCLUDE_DIRS]
            c_files.extend(
                os.path.join(root, f) 
                for f in files 
                if os.path.splitext(f)[1] in Config.SUPPORTED_EXTENSIONS
            )
        return c_files

    def get_metrics(self) -> List[Dict[str, float]]:
        """Возвращает собранные метрики для интеграции"""
        return self.aggregator.file_metrics

    def analyze_directory(self) -> None:
        """Анализ директории"""
        if not os.path.exists(self.path):
            logger.error(f"Ошибка: путь '{self.path}' не существует!")
            sys.exit(1)

        files = self._collect_files()
        logger.info(f"Найдено {len(files)} файлов для анализа...")
        
        with ThreadPoolExecutor() as executor:
            results = list(tqdm(
                executor.map(FileAnalyzer.analyze, files),
                total=len(files),
                desc="Анализ файлов"
            ))
        
        for metrics in filter(None, results):
            self.aggregator.add_file_metrics(metrics)

        try:
            ReportGenerator.generate_xml(
                self.aggregator.file_metrics, 
                self.output_xml
            )
        except Exception as e:
            logger.error(f"Не удалось сохранить отчёт: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Использование: python sourcemonitor_metrics.py <путь_к_директории>")
        sys.exit(1)

    analyzer = SourceMonitorMetrics(sys.argv[1])
    analyzer.analyze_directory()