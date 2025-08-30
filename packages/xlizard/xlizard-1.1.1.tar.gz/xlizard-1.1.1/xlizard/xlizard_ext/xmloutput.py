# xmloutput.py
'''
Thanks for Holy Wen from Nokia Siemens Networks to let me use his code
to put the result into xml file that is compatible with cppncss.
Jenkins has plugin for cppncss format result to display the diagram.
'''

import os
import re
from xlizard.combined_metrics import CombinedMetrics
from xlizard.sourcemonitor_metrics import SourceMonitorMetrics, FileAnalyzer, Config


def xml_output(all_result, verbose):
    """Generate extended XML report with SourceMonitor metrics"""
    result = all_result.result
    import xml.dom.minidom

    impl = xml.dom.minidom.getDOMImplementation()
    doc = impl.createDocument(None, "xlizard_metrics", None)
    root = doc.documentElement

    # Get SourceMonitor metrics - рекурсивный поиск файлов
    sm_metrics = {}
    if result and result[0].filename:
        try:
            # Получаем корневую директорию из первого файла
            project_root = os.path.dirname(result[0].filename)
            if verbose:
                print(f"Analyzing directory: {project_root}", file=__import__('sys').stderr)
            
            # Рекурсивно ищем все C/C++ файлы
            all_files = _find_all_source_files(project_root)
            if verbose:
                print(f"Found {len(all_files)} source files for analysis", file=__import__('sys').stderr)
            
            # Анализируем каждый файл
            for file_path in all_files:
                try:
                    metrics = FileAnalyzer.analyze(file_path)
                    if metrics:
                        # Нормализуем путь для consistent поиска
                        rel_path = os.path.relpath(file_path, project_root)
                        sm_metrics[file_path] = metrics
                        sm_metrics[rel_path] = metrics
                        sm_metrics[os.path.basename(file_path)] = metrics
                        if verbose:
                            print(f"Analyzed: {file_path}", file=__import__('sys').stderr)
                except Exception as e:
                    if verbose:
                        print(f"Error analyzing {file_path}: {e}", file=__import__('sys').stderr)
                        
        except Exception as e:
            if verbose:
                print(f"Warning: SourceMonitor metrics analysis failed: {e}", file=__import__('sys').stderr)

    # Create files section
    files_element = doc.createElement("files")
    root.appendChild(files_element)

    total_nloc = 0
    total_ccn = 0
    total_tokens = 0
    total_params = 0
    total_functions = 0
    total_files = 0

    for source_file in result:
        if source_file and source_file.filename:
            total_files += 1
            total_nloc += source_file.nloc
            total_ccn += source_file.CCN
            total_tokens += source_file.token_count
            total_functions += len(source_file.function_list)

            # Get SourceMonitor metrics for this file - улучшенный поиск
            file_key = os.path.normpath(source_file.filename)
            file_sm_metrics = None
            
            # Пробуем разные варианты поиска
            search_keys = [
                file_key,
                os.path.basename(file_key),
                os.path.abspath(file_key),
                os.path.relpath(file_key) if os.path.isabs(file_key) else file_key
            ]
            
            for key in search_keys:
                if key in sm_metrics:
                    file_sm_metrics = sm_metrics[key]
                    break
                    # Также пробуем поиск по частичному совпадению
                elif any(key.endswith(k) for k in sm_metrics.keys() if isinstance(k, str)):
                    for sm_key in sm_metrics.keys():
                        if isinstance(sm_key, str) and key.endswith(sm_key):
                            file_sm_metrics = sm_metrics[sm_key]
                            break

            file_element = doc.createElement("file")
            file_element.setAttribute("name", os.path.basename(source_file.filename))
            file_element.setAttribute("path", source_file.filename)
            files_element.appendChild(file_element)

            # File-level metrics
            _add_text_element(doc, file_element, "nloc", str(source_file.nloc))
            _add_text_element(doc, file_element, "ccn", str(source_file.CCN))
            _add_text_element(doc, file_element, "token_count", str(source_file.token_count))
            _add_text_element(doc, file_element, "functions_count", str(len(source_file.function_list)))
            
            # Calculate total parameters for file
            file_params = sum(len(func.parameters) for func in source_file.function_list)
            total_params += file_params
            _add_text_element(doc, file_element, "parameters_count", str(file_params))
            
            # SourceMonitor metrics for file
            if file_sm_metrics:
                _add_text_element(doc, file_element, "comment_percentage", 
                                 str(round(file_sm_metrics.get('comment_percentage', 0), 2)))
                _add_text_element(doc, file_element, "max_block_depth", 
                                 str(file_sm_metrics.get('max_block_depth', 0)))
                _add_text_element(doc, file_element, "pointer_operations", 
                                 str(file_sm_metrics.get('pointer_operations', 0)))
                _add_text_element(doc, file_element, "preprocessor_directives", 
                                 str(file_sm_metrics.get('preprocessor_directives', 0)))
            else:
                if verbose:
                    print(f"Warning: No SourceMonitor metrics found for {source_file.filename}", file=__import__('sys').stderr)
                # Добавляем пустые значения если метрики не найдены
                _add_text_element(doc, file_element, "comment_percentage", "0")
                _add_text_element(doc, file_element, "max_block_depth", "0")
                _add_text_element(doc, file_element, "pointer_operations", "0")
                _add_text_element(doc, file_element, "preprocessor_directives", "0")

            # Functions section
            if source_file.function_list:
                functions_element = doc.createElement("functions")
                file_element.appendChild(functions_element)

                for func in source_file.function_list:
                    function_element = doc.createElement("function")
                    function_element.setAttribute("name", func.name)
                    function_element.setAttribute("start_line", str(func.start_line))
                    function_element.setAttribute("end_line", str(func.end_line))
                    functions_element.appendChild(function_element)

                    # Function metrics from xlizard
                    _add_text_element(doc, function_element, "nloc", str(func.nloc))
                    _add_text_element(doc, function_element, "ccn", str(func.cyclomatic_complexity))
                    _add_text_element(doc, function_element, "token_count", str(func.token_count))
                    _add_text_element(doc, function_element, "parameter_count", str(func.parameter_count))
                    _add_text_element(doc, function_element, "length", str(func.length))
                    _add_text_element(doc, function_element, "max_nesting_depth", str(func.max_nesting_depth))

                    # Calculate SourceMonitor metrics for function
                    try:
                        func_code = _get_function_code(source_file.filename, func.start_line, func.end_line)
                        if func_code:
                            func_sm_metrics = _calculate_function_metrics(func_code)
                            _add_text_element(doc, function_element, "comment_percentage", 
                                             str(round(func_sm_metrics.get('comment_percentage', 0), 2)))
                            _add_text_element(doc, function_element, "max_block_depth", 
                                             str(func_sm_metrics.get('max_block_depth', 0)))
                            _add_text_element(doc, function_element, "pointer_operations", 
                                             str(func_sm_metrics.get('pointer_operations', 0)))
                            _add_text_element(doc, function_element, "preprocessor_directives", 
                                             str(_count_preprocessor_directives(func_code)))
                    except Exception as e:
                        if verbose:
                            print(f"Warning: Could not calculate function metrics for {func.name}: {e}", file=__import__('sys').stderr)
                        # Добавляем пустые значения при ошибке
                        _add_text_element(doc, function_element, "comment_percentage", "0")
                        _add_text_element(doc, function_element, "max_block_depth", "0")
                        _add_text_element(doc, function_element, "pointer_operations", "0")
                        _add_text_element(doc, function_element, "preprocessor_directives", "0")

    # Add summary section
    summary_element = doc.createElement("summary")
    root.appendChild(summary_element)

    _add_text_element(doc, summary_element, "total_files", str(total_files))
    _add_text_element(doc, summary_element, "total_nloc", str(total_nloc))
    _add_text_element(doc, summary_element, "total_ccn", str(total_ccn))
    _add_text_element(doc, summary_element, "total_tokens", str(total_tokens))
    _add_text_element(doc, summary_element, "total_parameters", str(total_params))
    _add_text_element(doc, summary_element, "total_functions", str(total_functions))
    
    if total_files > 0:
        _add_text_element(doc, summary_element, "average_nloc", str(round(total_nloc / total_files, 2)))
        _add_text_element(doc, summary_element, "average_ccn", str(round(total_ccn / total_files, 2)))
        _add_text_element(doc, summary_element, "average_tokens", str(round(total_tokens / total_files, 2)))
        _add_text_element(doc, summary_element, "average_parameters", str(round(total_params / total_files, 2)))
        _add_text_element(doc, summary_element, "average_functions_per_file", 
                         str(round(total_functions / total_files, 2)))

    return doc.toprettyxml()


def _find_all_source_files(directory):
    """Рекурсивно найти все C/C++ файлы в директории"""
    source_files = []
    exclude_dirs = {'.git', 'venv', '__pycache__', 'include', 'lib', 'bin'}
    
    try:
        for root, dirs, files in os.walk(directory):
            # Исключаем ненужные директории
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
            
            for file in files:
                if os.path.splitext(file)[1].lower() in {'.c', '.h', '.cpp', '.hpp', '.cc', '.cxx', '.hxx'}:
                    full_path = os.path.join(root, file)
                    source_files.append(full_path)
    except Exception as e:
        print(f"Error walking directory {directory}: {e}", file=__import__('sys').stderr)
    
    return source_files


def _add_text_element(doc, parent, name, value):
    """Helper to add text element"""
    element = doc.createElement(name)
    text = doc.createTextNode(value)
    element.appendChild(text)
    parent.appendChild(element)


def _get_function_code(file_path, start_line, end_line):
    """Get source code for a function"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            return ''.join(lines[start_line-1:end_line])
    except Exception as e:
        print(f"Error reading function code from {file_path}: {e}", file=__import__('sys').stderr)
        return ""


def _calculate_function_metrics(func_code):
    """Calculate SourceMonitor metrics for a function"""
    try:
        content_no_strings = FileAnalyzer._remove_string_literals(func_code)
        total_lines = len(func_code.split('\n'))
        comment_lines = FileAnalyzer._count_comments(func_code)
        
        return {
            'comment_percentage': (comment_lines / total_lines * 100) if total_lines else 0,
            'max_block_depth': FileAnalyzer._calculate_block_depth(content_no_strings, is_function=True),
            'pointer_operations': content_no_strings.count('*') + content_no_strings.count('&')
        }
    except Exception as e:
        print(f"Error calculating function metrics: {e}", file=__import__('sys').stderr)
        return {
            'comment_percentage': 0,
            'max_block_depth': 0,
            'pointer_operations': 0
        }


def _count_preprocessor_directives(code):
    """Count preprocessor directives in function code"""
    try:
        lines = code.split('\n')
        pp_directives = 0
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('#'):
                pp_directives += 1
        return pp_directives
    except Exception:
        return 0


# Keep original cppncss compatible output for backward compatibility
def cppncss_xml_output(all_result, verbose):
    """Original cppncss compatible XML output"""
    result = all_result.result
    import xml.dom.minidom

    impl = xml.dom.minidom.getDOMImplementation()
    doc = impl.createDocument(None, "cppncss", None)
    root = doc.documentElement

    processing_instruction = doc.createProcessingInstruction(
        'xml-stylesheet',
        'type="text/xsl" ' +
        'href="https://raw.githubusercontent.com' +
        '/terryyin/xlizard/master/xlizard.xsl"')
    doc.insertBefore(processing_instruction, root)

    root.appendChild(_create_function_measure(doc, result, verbose))
    root.appendChild(_create_file_measure(doc, result, all_result))

    return doc.toprettyxml()


def _create_function_measure(doc, result, verbose):
    measure = doc.createElement("measure")
    measure.setAttribute("type", "Function")
    measure.appendChild(_create_labels(doc, ["Nr.", "NCSS", "CCN"]))

    number = 0
    total_func_ncss = 0
    total_func_ccn = 0

    for source_file in result:
        if source_file:
            file_name = source_file.filename
            for func in source_file.function_list:
                number += 1
                total_func_ncss += func.nloc
                total_func_ccn += func.cyclomatic_complexity
                measure.appendChild(
                    _create_function_item(
                        doc, number, file_name, func, verbose))

            if number != 0:
                measure.appendChild(
                    _create_labeled_value_item(
                        doc, 'average', "NCSS", str(total_func_ncss / number)))
                measure.appendChild(
                    _create_labeled_value_item(
                        doc, 'average', "CCN", str(total_func_ccn / number)))
    return measure


def _create_file_measure(doc, result, all_result):
    all_in_one = all_result.as_fileinfo()
    measure = doc.createElement("measure")
    measure.setAttribute("type", "File")
    measure.appendChild(
        _create_labels(doc, ["Nr.", "NCSS", "CCN", "Functions"]))

    file_nr = 0
    file_total_ccn = 0
    file_total_funcs = 0

    for source_file in result:
        file_nr += 1
        file_total_ccn += source_file.CCN
        file_total_funcs += len(source_file.function_list)
        measure.appendChild(
            _create_file_node(doc, source_file, file_nr))

    if file_nr != 0:
        file_summary = [("NCSS", all_in_one.nloc / file_nr),
                        ("CCN", file_total_ccn / file_nr),
                        ("Functions", file_total_funcs / file_nr)]
        for key, val in file_summary:
            measure.appendChild(
                _create_labeled_value_item(doc, 'average', key, val))

    summary = [("NCSS", all_in_one.nloc),
               ("CCN", file_total_ccn),
               ("Functions", file_total_funcs)]
    for key, val in summary:
        measure.appendChild(_create_labeled_value_item(doc, 'sum', key, val))

    if file_total_funcs != 0:
        summary = [("NCSS", all_in_one.average_nloc),
                   ("CCN", all_in_one.average_cyclomatic_complexity)]
        for key, val in summary:
            measure.appendChild(_create_labeled_value_item(
                doc, 'average', key, val))

    return measure


def _create_label(doc, name):
    label = doc.createElement("label")
    text1 = doc.createTextNode(name)
    label.appendChild(text1)
    return label


def _create_labels(doc, label_name):
    labels = doc.createElement("labels")
    for label in label_name:
        labels.appendChild(_create_label(doc, label))

    return labels


def _create_function_item(doc, number, file_name, func, verbose):
    item = doc.createElement("item")
    if verbose:
        item.setAttribute(
            "name", "%s at %s:%s" %
            (func.long_name, file_name, func.start_line))
    else:
        item.setAttribute(
            "name", "%s(...) at %s:%s" %
            (func.name, file_name, func.start_line))
    value1 = doc.createElement("value")
    text1 = doc.createTextNode(str(number))
    value1.appendChild(text1)
    item.appendChild(value1)
    value2 = doc.createElement("value")
    text2 = doc.createTextNode(str(func.nloc))
    value2.appendChild(text2)
    item.appendChild(value2)
    value3 = doc.createElement("value")
    text3 = doc.createTextNode(str(func.cyclomatic_complexity))
    value3.appendChild(text3)
    item.appendChild(value3)
    return item


def _create_labeled_value_item(doc, name, label, value):
    average_ncss = doc.createElement(name)
    average_ncss.setAttribute("label", label)
    average_ncss.setAttribute("value", str(value))
    return average_ncss


def _create_file_node(doc, source_file, file_nr):
    item = doc.createElement("item")
    item.setAttribute("name", source_file.filename)
    value1 = doc.createElement("value")
    text1 = doc.createTextNode(str(file_nr))
    value1.appendChild(text1)
    item.appendChild(value1)
    value2 = doc.createElement("value")
    text2 = doc.createTextNode(str(source_file.nloc))
    value2.appendChild(text2)
    item.appendChild(value2)
    value3 = doc.createElement("value")
    text3 = doc.createTextNode(str(source_file.CCN))
    value3.appendChild(text3)
    item.appendChild(value3)
    value4 = doc.createElement("value")
    text4 = doc.createTextNode(str(len(source_file.function_list)))
    value4.appendChild(text4)
    item.appendChild(value4)
    return item