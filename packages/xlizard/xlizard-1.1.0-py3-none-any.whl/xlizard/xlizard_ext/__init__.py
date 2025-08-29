# __init__.py (в пакете расширений)
""" extensions of xlizard """

from __future__ import print_function
from .version import version
from .htmloutput import html_output
from .csvoutput import csv_output
from .xmloutput import xml_output
from .auto_open import auto_open, auto_read
from .checkstyleoutput import checkstyle_output
import os
import sys


def print_xml(results, options, _, total_factory):
    xml_content = xml_output(total_factory(list(results)), options.verbose)
    
    # Определяем путь для сохранения
    if hasattr(options, 'output_file') and options.output_file:
        output_path = options.output_file
        # Ensure the output file has .xml extension
        if not output_path.lower().endswith('.xml'):
            output_path += '.xml'
        output_dir = os.path.dirname(output_path)
    else:
        # По умолчанию сохраняем в output/xlizard_metrics.xml
        output_dir = "output"
        output_path = os.path.join(output_dir, "xlizard_metrics.xml")
    
    # Создаем директорию если не существует
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Сохраняем файл
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        print(f"XML report saved to: {output_path}", file=sys.stderr)
    except Exception as e:
        print(f"Error saving XML report to {output_path}: {e}", file=sys.stderr)
        # Fallback: print to stdout
        print(xml_content)
    
    return 0


def print_csv(results, options, _, total_factory):
    csv_output(total_factory(list(results)), options)
    return 0


def print_checkstyle(results, options, _, total_factory, file=None):
    import sys
    print("DEBUG: print_checkstyle called", file=sys.stderr)
    output = checkstyle_output(total_factory(list(results)), options.verbose)
    if file is None:
        file = sys.stdout
    file.write(output)
    if not output.endswith("\n"):
        file.write("\n")
    file.flush()
    return 0