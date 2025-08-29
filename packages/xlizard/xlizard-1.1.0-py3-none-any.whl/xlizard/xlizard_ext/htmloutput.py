from __future__ import print_function
import sys
import os
import datetime
from xlizard.combined_metrics import CombinedMetrics
from xlizard.sourcemonitor_metrics import SourceMonitorMetrics, Config
from xlizard.sourcemonitor_metrics import FileAnalyzer, Config

def html_output(result, options, *_):
    try:
        from jinja2 import Template
    except ImportError:
        sys.stderr.write(
                "HTML Output depends on jinja2. `pip install jinja2` first")
        sys.exit(2)

    # Get SourceMonitor metrics
    try:
        sm = SourceMonitorMetrics(options.paths[0] if options.paths else '.')
        sm.analyze_directory()
        
        # Create metrics dictionary with normalized paths
        sm_metrics = {}
        for m in sm.get_metrics():
            original_path = m['file_path']
            normalized_path = os.path.normpath(original_path)
            basename = os.path.basename(normalized_path)
            
            sm_metrics[normalized_path] = m
            sm_metrics[basename] = m
            sm_metrics[f"./{normalized_path}"] = m
            sm_metrics[normalized_path.replace('\\', '/')] = m
            
    except Exception as e:
        sys.stderr.write(f"Warning: SourceMonitor metrics not available ({str(e)})\n")
        sm_metrics = {}

    file_list = []
    for source_file in result:
        if source_file and not source_file.filename.endswith('.h'):
            file_key = os.path.normpath(source_file.filename)
            file_metrics = sm_metrics.get(file_key) or sm_metrics.get(os.path.basename(file_key))

            combined = CombinedMetrics(
                source_file,
                file_metrics
            )
            
            dirname = combined.dirname
            source_file_dict = {
                "filename": combined.filename,
                "basename": combined.basename,
                "dirname": dirname,
                "comment_percentage": file_metrics.get('comment_percentage', 0) if file_metrics else 0,
                "max_block_depth": file_metrics.get('max_block_depth', 0) if file_metrics else 0,
                "pointer_operations": file_metrics.get('pointer_operations', 0) if file_metrics else 0,
                "preprocessor_directives": file_metrics.get('preprocessor_directives', 0) if file_metrics else 0,
                "sourcemonitor": file_metrics
            }
            
            func_list = []
            max_complexity = 0
            for source_function in combined.functions:
                if source_function:
                    func_dict = _create_dict(source_function, source_file.filename)  # Передаём путь к файлу
                    func_dict['in_disable_block'] = _is_in_disable_block(
                        source_file.filename, 
                        source_function.start_line, 
                        source_function.end_line
                    )
                    if not hasattr(source_function, 'token_count'):
                        func_dict['token_count'] = 0
                    func_list.append(func_dict)
                    # Calculate max complexity for the file
                    if func_dict['cyclomatic_complexity'] > max_complexity:
                        max_complexity = func_dict['cyclomatic_complexity']
            
            source_file_dict["functions"] = func_list
            source_file_dict["max_complexity"] = max_complexity
            source_file_dict["avg_complexity"] = sum(
                func['cyclomatic_complexity'] for func in func_list
            ) / len(func_list) if func_list else 0
            file_list.append(source_file_dict)
    
    # Group files by directories
    dir_groups = {}
    for file in file_list:
        dirname = file['dirname']
        if dirname not in dir_groups:
            dir_groups[dirname] = []
        dir_groups[dirname].append(file)
    
    # Calculate metrics for dashboard
    complexity_data = []
    comment_data = []
    depth_data = []
    pointer_data = []
    directives_data = []
    
    for file in file_list:
        if file['functions']:
            complexity_data.extend([f['cyclomatic_complexity'] for f in file['functions']])
            comment_data.append(file['comment_percentage'])
            depth_data.append(file['max_block_depth'])
            pointer_data.append(file['pointer_operations'])
            directives_data.append(file['preprocessor_directives'])
    
    # Prepare comment distribution data
    comment_ranges = {
        '0-10': sum(1 for p in comment_data if p <= 10),
        '10-20': sum(1 for p in comment_data if 10 < p <= 20),
        '20-30': sum(1 for p in comment_data if 20 < p <= 30),
        '30-40': sum(1 for p in comment_data if 30 < p <= 40),
        '40-50': sum(1 for p in comment_data if 40 < p <= 50),
        '50+': sum(1 for p in comment_data if p > 50)
    }
    
    # Prepare depth vs pointers data
    depth_pointers_data = [
        {'x': f['pointer_operations'], 'y': f['max_block_depth'], 'file': f['basename']} 
        for f in file_list
    ]
    
    # Prepare complexity vs nloc data
    complexity_nloc_data = []
    top_complex_functions = []
    
    for file in file_list:
        for func in file['functions']:
            complexity_nloc_data.append({
                'x': func['nloc'],
                'y': func['cyclomatic_complexity'],
                'function': func['name'],
                'file': file['basename']
            })
            
            top_complex_functions.append({
                'name': func['name'],
                'complexity': func['cyclomatic_complexity'],
                'nloc': func['nloc'],
                'file': file['basename'],
                'filepath': file['filename']
            })
    
    # Get top 5 most complex functions
    top_complex_functions.sort(key=lambda x: -x['complexity'])
    top_complex_functions = top_complex_functions[:5]
    
    # Get files with min/max comments
    files_sorted_by_comments = sorted(file_list, key=lambda x: x['comment_percentage'])
    min_comments_files = files_sorted_by_comments[:5]
    max_comments_files = files_sorted_by_comments[-5:]
    max_comments_files.reverse()
    
    # Calculate code/comment/empty ratio
    total_lines = 0
    total_comments = 0
    total_empty = 0
    
    for file in file_list:
        if file.get('sourcemonitor'):
            total_lines += file['sourcemonitor'].get('lines_of_code', 0)
            total_comments += file['sourcemonitor'].get('comment_lines', 0)
            total_empty += file['sourcemonitor'].get('blank_lines', 0)
    
    code_ratio = {
        'code': total_lines,
        'comments': total_comments,
        'empty': total_empty
    }
    
    # Calculate directory complexity stats
    dir_complexity_stats = []
    for dirname, files in dir_groups.items():
        avg_complexity = sum(f['avg_complexity'] for f in files) / len(files) if files else 0
        dir_complexity_stats.append({
            'name': dirname,
            'avg_complexity': avg_complexity,
            'file_count': len(files)
        })
    
    # Sort directories by complexity
    dir_complexity_stats.sort(key=lambda x: -x['avg_complexity'])
    
    # Prepare dashboard data
    dashboard_data = {
        'complexity_distribution': {
            'low': sum(1 for c in complexity_data if c <= options.thresholds['cyclomatic_complexity'] * 0.5),
            'medium': sum(1 for c in complexity_data if options.thresholds['cyclomatic_complexity'] * 0.5 < c <= options.thresholds['cyclomatic_complexity']),
            'high': sum(1 for c in complexity_data if c > options.thresholds['cyclomatic_complexity'])
        },
        'avg_metrics': {
            'complexity': sum(complexity_data)/len(complexity_data) if complexity_data else 0,
            'comments': sum(comment_data)/len(comment_data) if comment_data else 0,
            'depth': sum(depth_data)/len(depth_data) if depth_data else 0,
            'pointers': sum(pointer_data)/len(pointer_data) if pointer_data else 0,
            'directives': sum(directives_data)/len(directives_data) if directives_data else 0
        },
        'comment_ranges': comment_ranges,
        'depth_pointers_data': depth_pointers_data,
        'complexity_nloc_data': complexity_nloc_data,
        'thresholds': options.thresholds
    }
    
    # Calculate metrics for files view
    total_complexity = 0
    total_functions = 0
    problem_files = 0
    total_comments = 0
    total_depth = 0
    total_pointers = 0
    total_directives = 0
    
    directory_stats = []
    
    for dirname, files in dir_groups.items():
        dir_complexity = 0
        dir_max_complexity = 0
        dir_functions = 0
        dir_problem_functions = 0
        dir_comments = 0
        dir_depth = 0
        dir_pointers = 0
        dir_directives = 0
        
        for file in files:
            file['problem_functions'] = sum(
                1 for func in file['functions'] 
                if func['cyclomatic_complexity'] > options.thresholds['cyclomatic_complexity']
            )
            file['max_complexity'] = max(
                (func['cyclomatic_complexity'] for func in file['functions']),
                default=0
            )
            file['avg_complexity'] = sum(
                func['cyclomatic_complexity'] for func in file['functions']
            ) / len(file['functions']) if file['functions'] else 0
            
            dir_complexity += file['avg_complexity']
            dir_max_complexity = max(dir_max_complexity, file['max_complexity'])
            dir_functions += len(file['functions'])
            dir_problem_functions += file['problem_functions']
            dir_comments += file['comment_percentage']
            dir_depth += file['max_block_depth']
            dir_pointers += file['pointer_operations']
            dir_directives += file['preprocessor_directives']
            
            total_complexity += file['avg_complexity']
            total_functions += len(file['functions'])
            total_comments += file['comment_percentage']
            total_depth += file['max_block_depth']
            total_pointers += file['pointer_operations']
            total_directives += file['preprocessor_directives']
            
            if file['max_complexity'] > options.thresholds['cyclomatic_complexity']:
                problem_files += 1
        
        directory_stats.append({
            'name': dirname,
            'max_complexity': dir_max_complexity,
            'avg_complexity': dir_complexity / len(files) if files else 0,
            'total_functions': dir_functions,
            'problem_functions': dir_problem_functions,
            'file_count': len(files),
            'avg_comments': dir_comments / len(files) if files else 0,
            'avg_depth': dir_depth / len(files) if files else 0,
            'avg_pointers': dir_pointers / len(files) if files else 0,
            'avg_directives': dir_directives / len(files) if files else 0
        })
    
    avg_complexity = total_complexity / len(file_list) if file_list else 0
    avg_comments = total_comments / len(file_list) if file_list else 0
    avg_depth = total_depth / len(file_list) if file_list else 0
    avg_pointers = total_pointers / len(file_list) if file_list else 0
    avg_directives = total_directives / len(file_list) if file_list else 0
    
    # Combine thresholds
    full_thresholds = {
        'cyclomatic_complexity': options.thresholds.get('cyclomatic_complexity', 15),
        'nloc': options.thresholds.get('nloc', 100),
        'comment_percentage': options.thresholds.get('comment_percentage', Config.THRESHOLDS['comment_percentage']),
        'max_block_depth': options.thresholds.get('max_block_depth', Config.THRESHOLDS['max_block_depth']),
        'pointer_operations': options.thresholds.get('pointer_operations', Config.THRESHOLDS['pointer_operations']),
        'preprocessor_directives': options.thresholds.get('preprocessor_directives', Config.THRESHOLDS['preprocessor_directives']),
        'parameter_count': 5,  # Жестко задаем порог в 5 параметров
        'function_count': 20,
        'token_count': 50
    }
    
    output = Template(TEMPLATE).render(
            title='xLizard + SourceMonitor code report',
            date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            thresholds=full_thresholds, 
            dir_groups=dir_groups,
            total_files=len(file_list),
            problem_files=problem_files,
            avg_complexity=round(avg_complexity, 2),
            avg_comments=round(avg_comments, 2),
            avg_depth=round(avg_depth, 2),
            avg_pointers=round(avg_pointers, 2),
            avg_directives=round(avg_directives, 2),
            total_functions=total_functions,
            directory_stats=sorted(directory_stats, key=lambda x: -x['max_complexity']),
            dashboard_data=dashboard_data,
            top_complex_functions=top_complex_functions,
            min_comments_files=min_comments_files,
            max_comments_files=max_comments_files,
            code_ratio=code_ratio,
            dir_complexity_stats=dir_complexity_stats)
    print(output)
    return 0

def _get_function_code(file_path, start_line, end_line):
    """Чтение кода функции с поддержкой разных кодировок"""
    try:
        # Пробуем разные кодировки
        encodings = ['utf-8', 'cp1251', 'latin-1', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                    lines = f.readlines()
                    return ''.join(lines[start_line-1:end_line])
            except UnicodeDecodeError:
                continue
        
        # Fallback: бинарное чтение
        with open(file_path, 'rb') as f:
            binary_content = f.read()
            content = binary_content.decode('utf-8', errors='ignore')
            lines = content.split('\n')
            return '\n'.join(lines[start_line-1:end_line])
            
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        return ""
    
def _create_dict(source_function, file_path):
    func_dict = {
        'name': source_function.name,
        'cyclomatic_complexity': source_function.cyclomatic_complexity,
        'nloc': source_function.nloc,
        'token_count': source_function.token_count,
        'parameter_count': source_function.parameter_count,
        'start_line': source_function.start_line,
        'end_line': source_function.end_line
    }
    
    # Получаем код функции
    func_code = _get_function_code(file_path, source_function.start_line, source_function.end_line)
    
    if func_code:
        # Используем прямое обращение к статическому методу
        func_dict['max_depth'] = FileAnalyzer._calculate_block_depth(func_code)
    else:
        func_dict['max_depth'] = 0
        
    # Проверяем, находится ли функция в disable-блоке
    func_dict['in_disable_block'] = _is_in_disable_block(file_path, source_function.start_line, source_function.end_line)
        
    return func_dict

def _is_in_disable_block(file_path, start_line, end_line):
    """Проверяет, находится ли функция между XLIZARD_DISABLE и XLIZARD_ENABLE"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        in_disable_block = False
        disable_start = 0
        
        # Проверяем все строки до начала функции
        for i, line in enumerate(lines[:start_line], 1):
            if 'XLIZARD_DISABLE' in line:
                in_disable_block = True
                disable_start = i
            elif 'XLIZARD_ENABLE' in line and in_disable_block:
                in_disable_block = False
                
        # Если функция начинается в disable-блоке, помечаем ее
        if in_disable_block:
            return True
            
        # Проверяем, не начинается ли disable-блок внутри функции
        for i, line in enumerate(lines[start_line-1:end_line], start_line):
            if 'XLIZARD_DISABLE' in line:
                return True
                
    except Exception:
        pass
        
    return False

TEMPLATE = '''<!DOCTYPE HTML PUBLIC
"-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ title }}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
  <style>
    :root {
        --glass-bg: rgba(255, 255, 255, 0.1);
        --glass-border: rgba(255, 255, 255, 0.15);
        --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        --glass-backdrop: blur(16px) saturate(180%);
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --success-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        --warning-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        --error-gradient: linear-gradient(135deg, #ff057c 0%, #8d0b93 100%);
        --text-primary: #ffffff;
        --text-secondary: rgba(255, 255, 255, 0.8);
        --text-tertiary: rgba(255, 255, 255, 0.6);
        --bg-primary: #0f0f1a;
        --bg-secondary: #1a1a2a;
        --bg-tertiary: #252536;
        --border-radius: 16px;
        --border-radius-sm: 8px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    [data-theme="light"] {
        --glass-bg: rgba(255, 255, 255, 0.8);
        --glass-border: rgba(0, 0, 0, 0.1);
        --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        --text-primary: #1a1a2a;
        --text-secondary: rgba(26, 26, 42, 0.8);
        --text-tertiary: rgba(26, 26, 42, 0.6);
        --bg-primary: #f8f9fa;
        --bg-secondary: #ffffff;
        --bg-tertiary: #f1f3f5;
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        background: var(--bg-primary);
        color: var(--text-primary);
        line-height: 1.6;
        min-height: 100vh;
        overflow-x: hidden;
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, var(--bg-tertiary) 100%);
        transition: var(--transition);
    }

    body::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 20%, rgba(103, 126, 234, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(247, 87, 108, 0.1) 0%, transparent 50%);
        pointer-events: none;
        z-index: -1;
        transition: var(--transition);
    }

    [data-theme="light"] body::before {
        background: 
            radial-gradient(circle at 20% 20%, rgba(103, 126, 234, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(247, 87, 108, 0.05) 0%, transparent 50%);
    }

    .container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem;
        min-height: 100vh;
    }

    /* Glass Header */
    .glass-header {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-backdrop);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius);
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: var(--glass-shadow);
        position: relative;
        overflow: hidden;
        transition: var(--transition);
    }

    .glass-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: var(--primary-gradient);
        opacity: 0.1;
        z-index: -1;
        animation: rotate 20s linear infinite;
    }

    /* Duck animations */
@keyframes duckFall {
    from {
        transform: translateY(-50px) rotate(0deg);
    }
    to {
        transform: translateY(100vh) rotate(360deg);
    }
}

@keyframes duckWobble {
    0%, 100% {
        transform: translateX(0px);
    }
    50% {
        transform: translateX(10px);
    }
}

.duck {
    animation: duckFall 5s linear infinite, duckWobble 2s ease-in-out infinite;
}

.duck:hover {
    animation-play-state: paused;
    transform: scale(1.2);
}

    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    .function-disabled {
        background: linear-gradient(135deg, rgba(255, 165, 0, 0.1) 0%, rgba(255, 140, 0, 0.2) 100%) !important;
        border-left: 4px solid #ff8c00;
    }

    .function-disabled:hover td {
        background: linear-gradient(135deg, rgba(255, 165, 0, 0.15) 0%, rgba(255, 140, 0, 0.25) 100%) !important;
    }

    .metric-value-warning {
        color: #ff8c00 !important;
        font-weight: 600;
    }

    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 2rem;
        position: relative;
        z-index: 2;
    }

    .header-text {
        flex: 1;
    }

    .logo-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .logo {
        width: 60px;
        height: 60px;
        background: var(--primary-gradient);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: bold;
        color: white;
        box-shadow: var(--glass-shadow);
    }

    .report-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        line-height: 1.1;
    }

    .report-subtitle {
        font-size: 1.2rem;
        color: var(--text-secondary);
        margin-bottom: 1.5rem;
    }

    .header-meta {
        display: flex;
        gap: 1.5rem;
        flex-wrap: wrap;
    }

    .meta-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--text-secondary);
        font-size: 0.95rem;
    }

    .header-actions {
        display: flex;
        gap: 1rem;
        align-items: center;
    }

    /* Glass Button */
    .glass-button {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-backdrop);
        border: 1px solid var(--glass-border);
        color: var(--text-primary);
        padding: 0.75rem 1.5rem;
        border-radius: var(--border-radius-sm);
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.95rem;
        font-weight: 500;
        transition: var(--transition);
        box-shadow: var(--glass-shadow);
    }

    .glass-button:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
    }

    /* Glass Navigation */
    .glass-nav {
        display: flex;
        background: var(--glass-bg);
        backdrop-filter: var(--glass-backdrop);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius);
        padding: 0.75rem;
        margin-bottom: 2rem;
        box-shadow: var(--glass-shadow);
        position: relative;
        overflow: hidden;
        gap: 0.75rem;
    }

    .glass-nav::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: var(--primary-gradient);
        opacity: 0.1;
        z-index: -1;
    }

    .nav-item {
        padding: 1rem 2rem;
        cursor: pointer;
        border-radius: var(--border-radius-sm);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        color: var(--text-secondary);
        font-weight: 500;
        position: relative;
        z-index: 2;
        border: none;
        background: none;
        flex: 1;
        text-align: center;
        margin: 0 0.25rem;
    }

    .nav-item:hover {
        color: var(--text-primary);
        background: rgba(255, 255, 255, 0.05);
        transform: translateY(-1px);
    }

    .nav-item.active {
        color: var(--text-primary);
        background: var(--glass-bg);
        box-shadow: 0 4px 20px 0 rgba(31, 38, 135, 0.4);
        font-weight: 600;
        transform: translateY(-2px);
    }

    .nav-item.active::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: var(--primary-gradient);
        border-radius: var(--border-radius-sm);
        z-index: -1;
        opacity: 0.3;
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.5; }
    }

    /* Glass Cards */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-backdrop);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius);
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: var(--glass-shadow);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }

    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: var(--primary-gradient);
        opacity: 0.05;
        z-index: -1;
    }

    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.4);
        border-color: rgba(255, 255, 255, 0.2);
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--glass-border);
    }

    .card-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .card-title::before {
        content: '';
        width: 8px;
        height: 8px;
        background: var(--primary-gradient);
        border-radius: 50%;
        display: inline-block;
    }

    /* Metrics Grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-backdrop);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius);
        padding: 2rem;
        text-align: center;
        transition: var(--transition);
        box-shadow: var(--glass-shadow);
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: var(--primary-gradient);
        opacity: 0.05;
        z-index: -1;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.4);
    }

    .metric-value {
        font-size: 3rem;
        font-weight: 700;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 1rem 0;
        line-height: 1;
    }

    .metric-label {
        font-size: 1rem;
        color: var(--text-secondary);
        margin: 0;
    }

    /* Charts Grid */
    .charts-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
        gap: 2rem;
        margin-bottom: 2rem;
    }

    .chart-container {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-backdrop);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius);
        padding: 2rem;
        box-shadow: var(--glass-shadow);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }

    .chart-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: var(--primary-gradient);
        opacity: 0.05;
        z-index: -1;
    }

    .chart-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.4);
    }

    .chart-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .chart-title::before {
        content: '';
        width: 6px;
        height: 6px;
        background: var(--secondary-gradient);
        border-radius: 50%;
        display: inline-block;
    }

    .chart-wrapper {
        position: relative;
        height: 300px;
        width: 100%;
    }

    /* Directory Groups */
    .directory-group {
        margin-bottom: 2.5rem;
    }

    .directory-header {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-backdrop);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius);
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--glass-shadow);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .directory-name {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .directory-name::before {
        content: '📁';
        font-size: 1.1rem;
    }

    .directory-count {
        background: var(--primary-gradient);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        color: white;
    }

    /* File Cards */
    .file-card {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-backdrop);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius);
        margin-bottom: 1.5rem;
        overflow: hidden;
        box-shadow: var(--glass-shadow);
        transition: var(--transition);
    }

    .file-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.4);
        border-color: rgba(255, 255, 255, 0.2);
    }

    .file-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 1.5rem 2rem;
        cursor: pointer;
        transition: var(--transition);
        background: rgba(255, 255, 255, 0.02);
        flex-direction: column;
        gap: 1rem;
    }

    .file-header:hover {
        background: rgba(255, 255, 255, 0.05);
    }

    .file-header.expanded {
        background: rgba(255, 255, 255, 0.08);
        border-bottom: 1px solid var(--glass-border);
    }

    .file-title {
        display: flex;
        align-items: center;
        gap: 1rem;
        width: 100%;
        min-width: 0;
        order: 1;
    }

    .file-icon {
        width: 24px;
        height: 24px;
        background: var(--primary-gradient);
        mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6z"/></svg>');
        -webkit-mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6z"/></svg>');
        mask-repeat: no-repeat;
        -webkit-mask-repeat: no-repeat;
        flex-shrink: 0;
    }

    .file-name {
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex: 1;
    }

    .file-metrics {
        display: flex;
        gap: 0.75rem;
        width: 100%;
        flex-wrap: wrap;
        order: 2;
    }

    /* Glass Badges */
    .glass-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        backdrop-filter: var(--glass-backdrop);
        transition: var(--transition);
        white-space: nowrap;
    }

    .glass-badge.safe {
        background: linear-gradient(135deg, rgba(67, 233, 123, 0.2) 0%, rgba(56, 249, 215, 0.2) 100%);
        border-color: rgba(67, 233, 123, 0.3);
        color: #43e97b;
    }

    .glass-badge.warning {
        background: linear-gradient(135deg, rgba(250, 112, 154, 0.2) 0%, rgba(254, 225, 64, 0.2) 100%);
        border-color: rgba(250, 112, 154, 0.3);
        color: #fa709a;
    }

    .glass-badge.danger {
        background: linear-gradient(135deg, rgba(255, 5, 124, 0.2) 0%, rgba(141, 11, 147, 0.2) 100%);
        border-color: rgba(255, 5, 124, 0.3);
        color: #ff057c;
    }

    .file-content {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(255, 255, 255, 0.02);
    }

    .file-content.expanded {
        max-height: 5000px;
    }

    .file-table {
        width: 100%;
        border-collapse: collapse;
    }

    .file-table th {
        text-align: left;
        padding: 1.5rem 2rem;
        font-weight: 600;
        color: var(--text-secondary);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background: rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid var(--glass-border);
    }

    .file-table td {
        padding: 1.25rem 2rem;
        border-bottom: 1px solid var(--glass-border);
        transition: var(--transition);
    }

    .file-table tr:last-child td {
        border-bottom: none;
    }

    .file-table tr:hover td {
        background: rgba(255, 255, 255, 0.03);
    }

    .function-name {
        font-family: 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
        color: var(--text-primary);
        font-size: 0.95rem;
        font-weight: 500;
    }

    .metric-value-high {
        color: #ff057c;
        font-weight: 600;
        animation: pulseText 2s ease-in-out infinite;
    }

    .metric-value-low {
        color: #43e97b;
        font-weight: 500;
    }

    @keyframes pulseText {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }

    /* Tooltips */
    .tooltip-icon {
        cursor: pointer;
        width: 18px;
        height: 18px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        color: var(--text-secondary);
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
        transition: var(--transition);
        backdrop-filter: var(--glass-backdrop);
    }

    .tooltip-icon:hover {
        background: var(--primary-gradient);
        color: white;
        border-color: transparent;
    }

    .custom-tooltip {
        position: absolute;
        z-index: 1000;
        background: var(--glass-bg);
        backdrop-filter: var(--glass-backdrop);
        border: 1px solid var(--glass-border);
        color: var(--text-primary);
        padding: 1rem 1.25rem;
        border-radius: var(--border-radius-sm);
        font-size: 0.9rem;
        max-width: 300px;
        box-shadow: var(--glass-shadow);
        opacity: 0;
        transform: translateY(10px);
        transition: var(--transition);
        pointer-events: none;
        line-height: 1.5;
    }

    .custom-tooltip.visible {
        opacity: 1;
        transform: translateY(0);
    }

    /* Footer */
    .glass-footer {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-backdrop);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius);
        padding: 2rem;
        margin-top: 3rem;
        text-align: center;
        color: var(--text-secondary);
        box-shadow: var(--glass-shadow);
    }

    /* Search Styles */
.glass-search {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-backdrop);
    border: 1px solid var(--glass-border);
    border-radius: var(--border-radius);
    padding: 1rem;
    margin-bottom: 2rem;
    box-shadow: var(--glass-shadow);
    position: relative;
    overflow: hidden;
}

.glass-search::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: var(--primary-gradient);
    opacity: 0.05;
    z-index: -1;
}

.search-container {
    display: flex;
    align-items: center;
    position: relative;
}

.search-icon {
    position: absolute;
    left: 12px;
    color: var(--text-secondary);
    z-index: 2;
}

.search-input {
    width: 100%;
    padding: 12px 40px 12px 40px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid var(--glass-border);
    border-radius: var(--border-radius-sm);
    color: var(--text-primary);
    font-family: inherit;
    font-size: 1rem;
    backdrop-filter: var(--glass-backdrop);
    transition: var(--transition);
}

.search-input:focus {
    outline: none;
    border-color: rgba(103, 126, 234, 0.5);
    background: rgba(255, 255, 255, 0.15);
    box-shadow: 0 0 0 3px rgba(103, 126, 234, 0.1);
}

.search-input::placeholder {
    color: var(--text-tertiary);
}

.clear-search {
    position: absolute;
    right: 12px;
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 4px;
    border-radius: 50%;
    transition: var(--transition);
    z-index: 2;
}

.clear-search:hover {
    color: var(--text-primary);
    background: rgba(255, 255, 255, 0.1);
}

/* Search highlight */
.highlight {
    background: linear-gradient(135deg, #ffd700 0%, #ffb700 100%);
    color: #000 !important;
    padding: 2px 4px;
    border-radius: 3px;
    font-weight: 600;
}

.search-match {
    animation: highlightPulse 2s ease-in-out;
}

@keyframes highlightPulse {
    0%, 100% { background-color: transparent; }
    50% { background-color: rgba(255, 215, 0, 0.3); }
}

    .glass-footer a {
        color: var(--text-primary);
        text-decoration: none;
        font-weight: 500;
        transition: var(--transition);
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .glass-footer a:hover {
        text-decoration: underline;
    }

    /* Tab Content */
    .tab-content {
        display: none;
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .tab-content.active {
        display: block;
        opacity: 1;
        transform: translateY(0);
    }

    @keyframes fadeIn {
        from { 
            opacity: 0;
            transform: translateY(20px);
        }
        to { 
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Responsive Design */
    @media (max-width: 1200px) {
        .charts-grid {
            grid-template-columns: 1fr;
        }
        
        .header-content {
            flex-direction: column;
            align-items: stretch;
        }
        
        .header-actions {
            justify-content: center;
        }
    }

    @media (max-width: 768px) {
        .container {
            padding: 1rem;
        }
        
        .glass-header {
            padding: 2rem 1.5rem;
        }
        
        .report-title {
            font-size: 2rem;
        }
        
        .metrics-grid {
            grid-template-columns: 1fr;
        }
        
        .file-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
        }
        
        .file-metrics {
            margin-left: 0;
            width: 100%;
            justify-content: flex-start;
        }
        
        .glass-nav {
            flex-direction: column;
            padding: 0.5rem;
            gap: 0.5rem;
        }
        
        .nav-item {
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
        }
    }

    @media (max-width: 480px) {
        .file-table {
            font-size: 0.85rem;
        }
        
        .file-table th,
        .file-table td {
            padding: 1rem 1.25rem;
        }
        
        .metric-value {
            font-size: 2.5rem;
        }
        
        .logo {
            width: 50px;
            height: 50px;
            font-size: 1.5rem;
        }
        
        .report-title {
            font-size: 1.8rem;
        }
        
        .glass-badge {
            padding: 0.4rem 0.8rem;
            font-size: 0.8rem;
        }
    }

    /* Animation for glass elements */
    @keyframes glassGlow {
        0%, 100% { opacity: 0.1; }
        50% { opacity: 0.2; }
    }

    .glass-card:hover::before,
    .metric-card:hover::before,
    .chart-container:hover::before {
        animation: glassGlow 2s ease-in-out infinite;
    }
  </style>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <!-- Glass Header -->
        <div class="glass-header">
            <div class="header-content">
                <div class="header-text">
                    <div class="logo-container">
                        <div class="logo">🦎</div>
                        <h1 class="report-title">{{ title }}</h1>
                    </div>
                    <p class="report-subtitle">Comprehensive code quality analysis with advanced metrics visualization</p>
                    <div class="header-meta">
                        <div class="meta-item">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                            </svg>
                            {{ total_files }} files analyzed
                        </div>
                        <div class="meta-item">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/>
                                <path d="M12.5 7H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
                            </svg>
                            {{ date }}
                        </div>
                    </div>
                </div>
                <div class="header-actions">
                    <button class="glass-button" id="themeToggle">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M20 8.69V4h-4.69L12 .69 8.69 4H4v4.69L.69 12 4 15.31V20h4.69L12 23.31 15.31 20H20v-4.69L23.31 12 20 8.69zM12 18c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6zm0-10c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4z"/>
                        </svg>
                        Toggle Theme
                    </button>
                </div>
            </div>
        </div>

        <!-- Glass Navigation -->
        <div class="glass-nav">
            <button class="nav-item active" data-tab="dashboardTab">Dashboard</button>
            <button class="nav-item" data-tab="filesTab">File Analysis</button>
            <button class="nav-item" data-tab="advancedTab">Advanced Metrics</button>
        </div>

        <div class="glass-search">
            <div class="search-container">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" class="search-icon">
                    <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                </svg>
                <input type="text" id="searchInput" placeholder="Search files and functions..." class="search-input">
                <button id="clearSearch" class="clear-search" style="display: none;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                </button>
            </div>
        </div>

        <!-- Dashboard Tab -->
        <div class="tab-content active" id="dashboardTab">
            <!-- Charts Grid -->
            <div class="charts-grid">
                <div class="chart-container">
                    <div class="chart-title">Complexity Distribution</div>
                    <div class="chart-wrapper">
                        <canvas id="complexityChart"></canvas>
                    </div>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Metrics Comparison</div>
                    <div class="chart-wrapper">
                        <canvas id="metricsChart"></canvas>
                    </div>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Comments Distribution</div>
                    <div class="chart-wrapper">
                        <canvas id="commentsChart"></canvas>
                    </div>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Depth vs Pointers Analysis</div>
                    <div class="chart-wrapper">
                        <canvas id="depthPointersChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Files Analysis Tab -->
        <div class="tab-content" id="filesTab">
            <!-- Code Quality Overview -->
            <div class="glass-card">
                <div class="card-header">
                    <h3 class="card-title">Code Quality Overview</h3>
                </div>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">Average Complexity</div>
                        <div class="metric-value">{{ avg_complexity|round(1) }}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Average Comments</div>
                        <div class="metric-value">{{ avg_comments|round(1) }}%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Average Depth</div>
                        <div class="metric-value">{{ avg_depth|round(1) }}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Total Functions</div>
                        <div class="metric-value">{{ total_functions }}</div>
                    </div>
                </div>
            </div>

            <!-- Project Files -->
            <div class="glass-card">
                <div class="card-header">
                    <h3 class="card-title">Project Files</h3>
                    <div class="directory-count">{{ total_files }} files</div>
                </div>
                
                {% for dirname, files in dir_groups.items() %}
                <div class="directory-group" id="dir-{{ dirname }}">
                    <div class="directory-header">
                        <h3 class="directory-name">{{ dirname }}</h3>
                        <div class="directory-count">{{ files|length }} file{{ 's' if files|length != 1 }}</div>
                    </div>
                    
                    {% for file in files %}
                    <div class="file-card">
                        <div class="file-header" onclick="toggleFile(this)">
                            <div class="file-title">
                                <div class="file-icon"></div>
                                <h4 class="file-name">{{ file.basename }}</h4>
                            </div>
                            <div class="file-metrics">
                                <div class="glass-badge {% if file.max_complexity <= thresholds['cyclomatic_complexity']*0.5 %}safe{% elif file.max_complexity <= thresholds['cyclomatic_complexity'] %}warning{% else %}danger{% endif %}">
                                    Max CC: {{ file.max_complexity }}
                                    <div class="tooltip-icon" data-tooltip="Thresholds: ≤{{ (thresholds['cyclomatic_complexity']*0.5)|round }} (safe), ≤{{ thresholds['cyclomatic_complexity'] }} (warning), >{{ thresholds['cyclomatic_complexity'] }} (danger)">?</div>
                                </div>
                                <div class="glass-badge {% if file.functions|length <= thresholds['function_count']*0.5 %}safe{% elif file.functions|length <= thresholds['function_count'] %}warning{% else %}danger{% endif %}">
                                    Max Funcs: {{ file.functions|length }}
                                    <div class="tooltip-icon" data-tooltip="Thresholds: ≤{{ (thresholds['function_count']*0.5)|round }} (safe), ≤{{ thresholds['function_count'] }} (warning), >{{ thresholds['function_count'] }} (danger)">?</div>
                                </div>
                                <div class="glass-badge {% if file.comment_percentage >= thresholds['comment_percentage']*1.2 %}safe{% elif file.comment_percentage >= thresholds['comment_percentage']*0.8 %}warning{% else %}danger{% endif %}">
                                   Max Comments: {{ file.comment_percentage|round(1) }}%
                                    <div class="tooltip-icon" data-tooltip="Thresholds: ≥{{ (thresholds['comment_percentage']*1.2)|round }}% (safe), ≥{{ (thresholds['comment_percentage']*0.8)|round }}% (warning), <{{ (thresholds['comment_percentage']*0.8)|round }}% (danger)">?</div>
                                </div>
                                <div class="glass-badge {% if file.max_block_depth <= thresholds['max_block_depth']*0.7 %}safe{% elif file.max_block_depth <= thresholds['max_block_depth'] %}warning{% else %}danger{% endif %}">
                                   Max Depth: {{ file.max_block_depth }}
                                    <div class="tooltip-icon" data-tooltip="Thresholds: ≤{{ (thresholds['max_block_depth']*0.7)|round }} (safe), ≤{{ thresholds['max_block_depth'] }} (warning), >{{ thresholds['max_block_depth'] }} (danger)">?</div>
                                </div>
                                <div class="glass-badge {% if file.pointer_operations <= thresholds['pointer_operations']*0.5 %}safe{% elif file.pointer_operations <= thresholds['pointer_operations'] %}warning{% else %}danger{% endif %}">
                                  Max  Ptr Ops: {{ file.pointer_operations }}
                                    <div class="tooltip-icon" data-tooltip="Thresholds: ≤{{ (thresholds['pointer_operations']*0.5)|round }} (safe), ≤{{ thresholds['pointer_operations'] }} (warning), >{{ thresholds['pointer_operations'] }} (danger)">?</div>
                                </div>
                                <div class="glass-badge {% if file.preprocessor_directives <= thresholds['preprocessor_directives']*0.5 %}safe{% elif file.preprocessor_directives <= thresholds['preprocessor_directives'] %}warning{% else %}danger{% endif %}">
                                   Max PP Directives: {{ file.preprocessor_directives }}
                                    <div class="tooltip-icon" data-tooltip="Thresholds: ≤{{ (thresholds['preprocessor_directives']*0.5)|round }} (safe), ≤{{ thresholds['preprocessor_directives'] }} (warning), >{{ thresholds['preprocessor_directives'] }} (danger)">?</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="file-content">
                            {% if file.functions|length > 0 %}
                            <table class="file-table">
                                <thead>
                                    <tr>
                                        <th>Function</th>
                                        <th>
                                            CCN <div class="tooltip-icon" data-tooltip="Cyclomatic Complexity Number">?</div>
                                        </th>
                                        <th>
                                            LOC <div class="tooltip-icon" data-tooltip="Lines of Code">?</div>
                                        </th>
                                        <th>
                                            Tokens <div class="tooltip-icon" data-tooltip="Number of tokens">?</div>
                                        </th>
                                        <th>
                                            Params <div class="tooltip-icon" data-tooltip="Number of parameters">?</div>
                                        </th>
                                        <th>
                                            Depth <div class="tooltip-icon" data-tooltip="Maximum nesting depth">?</div>
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for func in file.functions %}
                                    <tr class="{% if func.in_disable_block %}function-disabled{% endif %}">
                                        <td class="function-name">
                                            {{ func.name }}
                                            {% if func.in_disable_block %}
                                            <div class="tooltip-icon" data-tooltip="Function analysis disabled by XLIZARD_DISABLE directive">🟠</div>
                                            {% endif %}
                                        </td>
                                        <td class="{% if func.in_disable_block %}metric-value-warning{% elif func.cyclomatic_complexity > thresholds['cyclomatic_complexity'] %}metric-value-high{% else %}metric-value-low{% endif %}">
                                            {{ func.cyclomatic_complexity }}
                                        </td>
                                        <td class="{% if func.in_disable_block %}metric-value-warning{% elif func.nloc > thresholds['nloc'] %}metric-value-high{% else %}metric-value-low{% endif %}">
                                            {{ func.nloc }}
                                        </td>
                                        <td class="{% if func.in_disable_block %}metric-value-warning{% elif func.token_count > thresholds['token_count'] %}metric-value-high{% else %}metric-value-low{% endif %}">
                                            {{ func.token_count }}
                                        </td>
                                        <td class="{% if func.in_disable_block %}metric-value-warning{% elif func.parameter_count > thresholds['parameter_count'] %}metric-value-high{% else %}metric-value-low{% endif %}">
                                            {{ func.parameter_count }}
                                        </td>
                                        <td class="{% if func.in_disable_block %}metric-value-warning{% elif func.max_depth > thresholds['max_block_depth'] %}metric-value-high{% else %}metric-value-low{% endif %}">
                                            {{ func.max_depth }}
                                        </td>
                                    </tr>
                                {% endfor %}
                                </tbody>
                            </table>
                            {% else %}
                            <div style="padding: 3rem; text-align: center; color: var(--text-secondary);">
                                <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" style="opacity: 0.5; margin-bottom: 1rem;">
                                    <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zM6 20V4h7v5h5v11H6z"/>
                                </svg>
                                <p>No functions found in this file</p>
                            </div>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Advanced Metrics Tab -->
        <div class="tab-content" id="advancedTab">
            <div class="charts-grid">
                <div class="chart-container">
                    <div class="chart-title">Complexity vs Lines of Code</div>
                    <div class="chart-wrapper">
                        <canvas id="complexityNlocChart"></canvas>
                    </div>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Code Composition</div>
                    <div class="chart-wrapper">
                        <canvas id="codeCompositionChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="glass-card">
                <div class="card-header">
                    <h3 class="card-title">Directory Complexity Heatmap</h3>
                </div>
                <div class="chart-wrapper">
                    <div id="heatmapChart" style="height: 400px;"></div>
                </div>
            </div>

            <div class="glass-card">
                <div class="card-header">
                    <h3 class="card-title">Top 5 Most Complex Functions</h3>
                </div>
                <div style="overflow-x: auto;">
                    <table class="file-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Function</th>
                                <th>File</th>
                                <th>Complexity</th>
                                <th>Lines</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for func in top_complex_functions %}
                            <tr>
                                <td>{{ loop.index }}</td>
                                <td class="function-name">{{ func.name }}</td>
                                <td>{{ func.file }}</td>
                                <td class="metric-value-high">{{ func.complexity }}</td>
                                <td>{{ func.nloc }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="glass-card">
                <div class="card-header">
                    <h3 class="card-title">Files with Lowest Comments</h3>
                </div>
                <div style="overflow-x: auto;">
                    <table class="file-table">
                        <thead>
                            <tr>
                                <th>File</th>
                                <th>Comment %</th>
                                <th>Complexity</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for file in min_comments_files %}
                            <tr>
                                <td>{{ file.basename }}</td>
                                <td class="metric-value-high">{{ file.comment_percentage|round(1) }}%</td>
                                <td>{{ file.max_complexity }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="glass-card">
                <div class="card-header">
                    <h3 class="card-title">Files with Highest Comments</h3>
                </div>
                <div style="overflow-x: auto;">
                    <table class="file-table">
                        <thead>
                            <tr>
                                <th>File</th>
                                <th>Comment %</th>
                                <th>Complexity</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for file in max_comments_files %}
                            <tr>
                                <td>{{ file.basename }}</td>
                                <td class="metric-value-low">{{ file.comment_percentage|round(1) }}%</td>
                                <td>{{ file.max_complexity }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="glass-card">
                <div class="card-header">
                    <h3 class="card-title">Average Complexity by Directory</h3>
                </div>
                <div style="overflow-x: auto;">
                    <table class="file-table">
                        <thead>
                            <tr>
                                <th>Directory</th>
                                <th>Avg Complexity</th>
                                <th>Files</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for dir in dir_complexity_stats %}
                            <tr>
                                <td>{{ dir.name }}</td>
                                <td class="{% if dir.avg_complexity > thresholds['cyclomatic_complexity'] %}metric-value-high{% else %}metric-value-low{% endif %}">
                                    {{ dir.avg_complexity|round(1) }}
                                </td>
                                <td>{{ dir.file_count }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="glass-card">
                <div class="card-header">
                    <h3 class="card-title">Code Hotspots Analysis</h3>
                </div>
                <div style="padding: 1.5rem;">
                    <div style="display: flex; flex-wrap: wrap; gap: 0.75rem;">
                        {% for file in file_list %}
                            {% if file.max_complexity > thresholds['cyclomatic_complexity'] and file.comment_percentage < thresholds['comment_percentage']*0.5 %}
                            <div class="glass-badge danger">
                                {{ file.basename }} (CC: {{ file.max_complexity }}, Comments: {{ file.comment_percentage|round(1) }}%)
                            </div>
                            {% endif %}
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>

        <div class="glass-footer">
            Generated on {{ date }} by <a href="http://www.xlizard.ws/" target="_blank">xlizard</a> with SourceMonitor metrics
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize dashboard charts immediately
        initDashboardCharts();
        window.chartsInitialized = true;

        // Theme toggle functionality
        const themeToggle = document.getElementById('themeToggle');
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.body.getAttribute('data-theme') || 'dark';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Update charts with new theme
            updateChartsTheme();
        });

        // Set initial theme
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.body.setAttribute('data-theme', savedTheme);

        // Tooltip system
        const tooltip = document.createElement('div');
        tooltip.className = 'custom-tooltip';
        document.body.appendChild(tooltip);

        document.querySelectorAll('.tooltip-icon').forEach(icon => {
            icon.addEventListener('mouseenter', function(e) {
                const text = this.getAttribute('data-tooltip');
                const rect = this.getBoundingClientRect();
                
                tooltip.textContent = text;
                tooltip.style.left = `${rect.left + window.scrollX}px`;
                tooltip.style.top = `${rect.top + window.scrollY - tooltip.offsetHeight - 10}px`;
                tooltip.classList.add('visible');
            });

            icon.addEventListener('mouseleave', function() {
                tooltip.classList.remove('visible');
            });
        });

        // Navigation system
        const navItems = document.querySelectorAll('.nav-item');
        const tabContents = document.querySelectorAll('.tab-content');

        function switchTab(tabId) {
            // Remove active class from all nav items and tabs
            navItems.forEach(nav => nav.classList.remove('active'));
            tabContents.forEach(tab => tab.classList.remove('active'));
            
            // Add active class to clicked item
            document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
            document.getElementById(tabId).classList.add('active');
            
            // Initialize charts if needed
            if (tabId === 'advancedTab' && !window.advancedChartsInitialized) {
                setTimeout(initAdvancedCharts, 100);
                window.advancedChartsInitialized = true;
            }
        }

        navItems.forEach(item => {
            item.addEventListener('click', function() {
                const tabId = this.getAttribute('data-tab');
                switchTab(tabId);
            });
        });

        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const clearSearch = document.getElementById('clearSearch');

        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase().trim();
            clearSearch.style.display = searchTerm ? 'block' : 'none';
            
            // Remove previous highlights
            document.querySelectorAll('.highlight').forEach(el => {
                el.outerHTML = el.innerHTML;
            });
            
            let hasAnyMatch = false;
            let firstMatchElement = null;
            
            if (searchTerm) {
                // Search in file names
                document.querySelectorAll('.file-name').forEach(element => {
                    const filename = element.textContent.toLowerCase();
                    if (filename.includes(searchTerm)) {
                        const highlighted = element.textContent.replace(
                            new RegExp(searchTerm, 'gi'), 
                            match => `<span class="highlight">${match}</span>`
                        );
                        element.innerHTML = highlighted;
                        const fileCard = element.closest('.file-card');
                        fileCard.classList.add('search-match');
                        hasAnyMatch = true;
                        
                        // Auto-expand file
                        const fileHeader = fileCard.querySelector('.file-header');
                        if (fileHeader && !fileHeader.classList.contains('expanded')) {
                            toggleFile(fileHeader);
                        }
                        
                        // Remember first match for scrolling
                        if (!firstMatchElement) {
                            firstMatchElement = fileCard;
                        }
                    }
                });
                
                // Search in function names
                document.querySelectorAll('.function-name').forEach(element => {
                    const funcName = element.textContent.toLowerCase();
                    if (funcName.includes(searchTerm)) {
                        const highlighted = element.textContent.replace(
                            new RegExp(searchTerm, 'gi'), 
                            match => `<span class="highlight">${match}</span>`
                        );
                        element.innerHTML = highlighted;
                        const fileCard = element.closest('.file-card');
                        fileCard.classList.add('search-match');
                        hasAnyMatch = true;
                        
                        // Auto-expand file
                        const fileHeader = fileCard.querySelector('.file-header');
                        if (fileHeader && !fileHeader.classList.contains('expanded')) {
                            toggleFile(fileHeader);
                        }
                        
                        // Remember first match for scrolling
                        if (!firstMatchElement) {
                            firstMatchElement = element;
                        }
                    }
                });
                
                // Hide files without matches
                document.querySelectorAll('.file-card').forEach(card => {
                    const hasMatch = card.querySelector('.highlight') !== null;
                    card.style.display = hasMatch ? '' : 'none';
                });
                
                // Scroll to first match
                if (firstMatchElement) {
                    setTimeout(() => {
                        firstMatchElement.scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });
                    }, 100);
                }
            } else {
                // Show all files, remove highlights, and collapse all
                document.querySelectorAll('.file-card').forEach(card => {
                    card.style.display = '';
                    card.classList.remove('search-match');
                    
                    // Collapse file if it was expanded by search
                    const fileHeader = card.querySelector('.file-header');
                    if (fileHeader && fileHeader.classList.contains('expanded')) {
                        toggleFile(fileHeader);
                    }
                });
            }
        });

        clearSearch.addEventListener('click', function() {
            searchInput.value = '';
            this.style.display = 'none';
            
            // Remove all highlights, show all files, and collapse all
            document.querySelectorAll('.highlight').forEach(el => {
                el.outerHTML = el.innerHTML;
            });
            
            document.querySelectorAll('.file-card').forEach(card => {
                card.style.display = '';
                card.classList.remove('search-match');
                
                // Collapse file if it was expanded by search
                const fileHeader = card.querySelector('.file-header');
                if (fileHeader && fileHeader.classList.contains('expanded')) {
                    toggleFile(fileHeader);
                }
            });
        });

        // Handle Escape key for search
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && searchInput.value) {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
            }
        });

        // Auto-switch to Files tab when searching
        searchInput.addEventListener('focus', function() {
            if (this.value) {
                switchTab('filesTab');
            }
        });
    });

    // File toggle function
    function toggleFile(header) {
        const content = header.nextElementSibling;
        const isExpanding = !header.classList.contains('expanded');
        
        header.classList.toggle('expanded');
        content.classList.toggle('expanded');
        
        if (isExpanding) {
            content.style.maxHeight = content.scrollHeight + 'px';
        } else {
            content.style.maxHeight = '0';
        }
    }

    // Dashboard Charts initialization
    function initDashboardCharts() {
        const dashboardData = {{ dashboard_data|tojson }};
        const isDark = document.body.getAttribute('data-theme') === 'dark';
        const textColor = isDark ? '#ffffff' : '#1a1a2a';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        const fontFamily = 'Inter, sans-serif';

        // Complexity Distribution Chart
        const complexityCtx = document.getElementById('complexityChart').getContext('2d');
        new Chart(complexityCtx, {
            type: 'doughnut',
            data: {
                labels: ['Low Complexity', 'Medium Complexity', 'High Complexity'],
                datasets: [{
                    data: [
                        dashboardData.complexity_distribution.low,
                        dashboardData.complexity_distribution.medium,
                        dashboardData.complexity_distribution.high
                    ],
                    backgroundColor: ['#43e97b', '#fa709a', '#ff057c'],
                    borderColor: isDark ? '#1a1a2a' : '#ffffff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: textColor,
                            font: {
                                family: fontFamily,
                                size: 12
                            }
                        }
                    }
                },
                cutout: '70%'
            }
        });

        // Metrics Comparison Chart
        const metricsCtx = document.getElementById('metricsChart').getContext('2d');
        new Chart(metricsCtx, {
            type: 'bar',
            data: {
                labels: ['Complexity', 'Comments', 'Depth', 'Pointers', 'Directives'],
                datasets: [{
                    label: 'Average Value',
                    data: [
                        dashboardData.avg_metrics.complexity,
                        dashboardData.avg_metrics.comments,
                        dashboardData.avg_metrics.depth,
                        dashboardData.avg_metrics.pointers,
                        dashboardData.avg_metrics.directives
                    ],
                    backgroundColor: 'rgba(103, 126, 234, 0.8)',
                    borderColor: 'rgba(103, 126, 234, 1)',
                    borderWidth: 1
                }, {
                    label: 'Threshold',
                    data: [
                        dashboardData.thresholds.cyclomatic_complexity,
                        dashboardData.thresholds.comment_percentage,
                        dashboardData.thresholds.max_block_depth,
                        dashboardData.thresholds.pointer_operations,
                        dashboardData.thresholds.preprocessor_directives
                    ],
                    backgroundColor: 'rgba(255, 255, 255, 0.3)',
                    borderColor: 'rgba(255, 255, 255, 0.5)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor,
                            font: {
                                family: fontFamily
                            }
                        }
                    },
                    x: {
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor,
                            font: {
                                family: fontFamily
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: textColor,
                            font: {
                                family: fontFamily
                            }
                        }
                    }
                }
            }
        });

        // Comments Distribution Chart
        const commentsCtx = document.getElementById('commentsChart').getContext('2d');
        new Chart(commentsCtx, {
            type: 'polarArea',
            data: {
                labels: Object.keys(dashboardData.comment_ranges).map(k => k.replace('-', '-') + '%'),
                datasets: [{
                    data: Object.values(dashboardData.comment_ranges),
                    backgroundColor: [
                        'rgba(103, 126, 234, 0.7)',
                        'rgba(67, 233, 123, 0.7)',
                        'rgba(250, 112, 154, 0.7)',
                        'rgba(255, 5, 124, 0.7)',
                        'rgba(79, 172, 254, 0.7)',
                        'rgba(141, 11, 147, 0.7)'
                    ],
                    borderColor: isDark ? '#1a1a2a' : '#ffffff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: textColor,
                            font: {
                                family: fontFamily
                            }
                        }
                    }
                }
            }
        });

        // Depth vs Pointers Chart
        const depthPointersCtx = document.getElementById('depthPointersChart').getContext('2d');
        new Chart(depthPointersCtx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Files',
                    data: dashboardData.depth_pointers_data,
                    backgroundColor: 'rgba(103, 126, 234, 0.7)',
                    borderColor: 'rgba(103, 126, 234, 1)',
                    borderWidth: 1,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: 'Block Depth',
                            color: textColor,
                            font: {
                                family: fontFamily
                            }
                        },
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor,
                            font: {
                                family: fontFamily
                            }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Pointer Operations',
                            color: textColor,
                            font: {
                                family: fontFamily
                            }
                        },
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor,
                            font: {
                                family: fontFamily
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `File: ${context.raw.file}`;
                            },
                            afterLabel: function(context) {
                                return `Depth: ${context.raw.y}\nPointers: ${context.raw.x}`;
                            }
                        }
                    }
                }
            }
        });
    }

    function updateChartsTheme() {
        if (window.chartsInitialized) {
            initDashboardCharts();
        }
        if (window.advancedChartsInitialized) {
            initAdvancedCharts();
        }
    }
</script>

<!-- Duck Easter Egg -->
<div id="duckCounter" style="display: none; position: fixed; top: 20px; right: 20px; z-index: 9999; 
    background: var(--glass-bg); backdrop-filter: var(--glass-backdrop); border: 1px solid var(--glass-border); 
    padding: 10px 15px; border-radius: 20px; color: var(--text-primary); font-weight: bold; font-size: 16px;">
    Ducks: <span id="duckScore">0</span>
</div>

<div id="gameOver" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
    background: rgba(0, 0, 0, 0.9); z-index: 10000; color: white; font-size: 48px; font-weight: bold;
    display: none; justify-content: center; align-items: center; flex-direction: column;">
    <div>YOU DEAD</div>
    <div style="font-size: 24px; margin-top: 20px;">Score: <span id="finalScore">0</span></div>
    <button onclick="resetGame()" style="margin-top: 30px; padding: 10px 20px; font-size: 18px;
        background: #ff4757; border: none; border-radius: 10px; color: white; cursor: pointer;">
        Try Again
    </button>
</div>

<script>
    // Duck Easter Egg
    let duckSequence = '';
    let activeDucks = new Set();
    let duckScore = 0;
    let missedDucks = 0;
    let gameActive = false;
    let duckInterval = null;

    // SVG утки в base64
    const duckSVG = 'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iaXNvLTg4NTktMSI/Pgo8c3ZnIGhlaWdodD0iNjAiIHdpZHRoPSI2MCIgdmlld0JveD0iMCAwIDUxMiA1MTIiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnPgoJPHBhdGggZmlsbD0iI0QxODc3MCIgZD0iTTkwLjQ2NSwxODYuOTEyYzAuMDg2LTcuNTgxLTUuMjYtMjcuNDksMi43NzEtNDMuNzgxYzguMDI1LTE2LjI5MS00Mi4yMjYtMjAuNTQ2LTY3LjY4MiwwLjM2NwoJCWMtMjQuNTEsMjAuMTM3LDEuNzY0LDM3LjQ2OCwxNy45MzgsMzMuNjU3Qzc2LjI2NywxNjkuNDI4LDkwLjI5OSwyMDIuMjYxLDkwLjQ2NSwxODYuOTEyeiIvPgoJPHBhdGggZmlsbD0iI0REODk2OCIgZD0iTTczLjMxNSw5Ni4wMDljMC4wNzksNy41NzQtNS4yNiwyNy40ODMsMi43NjQsNDMuNzgyYzguMDI1LDE2LjI3Ny00Ni43OTksMjUuMTA1LTY3LjY3NC0wLjM3NQoJCWMtMjAuODc4LTI1LjQ4LDEuNzYtMzcuNDYxLDE3Ljk0MS0zMy42NUM1OS4xMDIsMTEzLjQ4NSw3My4xMzcsODAuNjU0LDczLjMxNSw5Ni4wMDl6Ii8+Cgk8cGF0aCBmaWxsPSIjRjZFMTc0IiBkPSJNNzYuNDUsMjY0LjIxMWMxOC4xODMtMjEuNDA2LDMzLjA5Mi0zMS4wMzgsMjAuODIxLTUwLjQzMwoJCWMtMjMuNDAyLTIzLjQwOC0zNC4zMDktNDguNzQzLTM0LjMwOS04NC40NThjMC0zNS43MDksMTQuNDc2LTY4LjAzNSwzNy44NzYtOTEuNDM2QzEyNC4yNDMsMTQuNDgzLDE1Ni41NjMsMCwxOTIuMjc4LDAKCQlzNjguMDM1LDE0LjQ4Myw5MS40NDMsMzcuODg0YzIzLjQwMSwyMy40MDIsMzcuODcsNTUuNzI4LDM3Ljg3LDkxLjQzNmMwLDUyLjc4OS00Mi4yMjIsOTUuMDExLTQyLjIyMiwxMjEuNAoJCWMtMi42NCwxMC41NjEsMTUuODM1LDIzLjc2MSwzOS41ODIsMjMuNzYxYzIzLjc2MSwwLDEwMi45MzIsMTguNDY3LDE2MC45ODgtNTguMDYzYzE1LjI4LTIxLjEyMiwzMy43NTUtOS4yMzgsMzEuNjc1LDIxLjEwNwoJCUM1MDkuNjE4LDI2Ni42MDksNDkzLjEzMyw1MTIsMzE4Ljk1MSw1MTJjLTUwLjEzNSwwLTQzLjc4OCwwLTEzOS44NzQsMGMtNDAuMDc0LDAtNzYuMzYtMTYuMjUtMTAyLjYyNy00Mi41MTMKCQljLTI2LjI3My0yNi4yNy00Mi41Mi02Mi41NTQtNDIuNTItMTAyLjY0OUMzMy45MywzMjYuNzY1LDUwLjE3NiwyOTAuNDc0LDc2LjQ1LDI2NC4yMTEiLz4KCTxwYXRoIGZpbGw9IiVFNUQyOUIiIGQ9Ik0yMTkuNTMzLDM0MC40NThoMTkzLjIxNmMyMS4xMDgsMCwyNi4zODgsMzYuOTQxLTcuOTIsNTguMDYzYzAsMjYuMzgtMTMuMjAxLDY1Ljk3LTUyLjc4Miw2NS45NwoJCWMtMzkuNTk2LDAtODcuMDkyLDAtMTIxLjQsMGMtMzQuMzE2LDAtNTguMDY0LTM5LjU5LTU4LjA2NC02My4zMzdDMTcyLjU4NCwzNzcuMzk5LDE5NS43NzcsMzQwLjQ1OCwyMTkuNTMzLDM0MC40NTh6Ii8+Cgk8cGF0aCBmaWxsPSIjRjBENzgwIiBkPSJNMjA2LjMzMSwzMjQuNjE2aDE5My4yMThjMjEuMTA4LDAsMjYuMzg4LDM2Ljk0OS03LjkyLDU4LjA2NGMwLDI2LjM5NS0xMy4xOTQsNjUuOTgzLTUyLjc3Niw2NS45ODMKCQljLTM5LjU4OSwwLTg3LjA5NywwLTEyMS40MDYsMHMtNTguMDU3LTM5LjU4OS01OC4wNTctNjMuMzQ0QzE1OS4zOSwzNjEuNTY1LDE4Mi41ODMsMzI0LjYxNiwyMDYuMzMxLDMyNC42MTZ6Ii8+Cgk8cGF0aCBmaWxsPSIjRkZGRkZGIiBkPSJNMTU5LjM5LDEwOS41MjJjMCwxNi43Ny0xMy41OTYsMzAuMzU5LTMwLjM0OCwzMC4zNTljLTE2Ljc2MywwLTMwLjM1NS0xMy41ODktMzAuMzU1LTMwLjM1OQoJCWMwLTE2Ljc0OCwxMy41OTItMzAuMzQ0LDMwLjM1NS0zMC4zNDRDMTQ1Ljc5NCw3OS4xNzcsMTU5LjM5LDkyLjc3MywxNTkuMzksMTA5LjUyMnoiLz4KCTxwYXRoIGZpbGw9IiM2NDYzNjMiIGQ9Ik0xNDMuNTU2LDEwOS41MjJjMCw4LjAyNS02LjUwMywxNC41MjUtMTQuNTE0LDE0LjUyNWMtOC4wMTgsMC0xNC41MTgtNi41LTE0LjUxOC0xNC41MjUKCQljMC04LjAwMyw2LjUtMTQuNTAzLDE0LjUxOC0xNC41MDNDMTM3LjA1Miw5NS4wMTgsMTQ3LjU1NiwxMDEuNTE4LDE0My41NTYsMTA5LjUyMnoiLz4KPC9nPgo8L3N2Zz4K';

    document.addEventListener('keydown', function(e) {
        // Add pressed key to sequence (only letters)
        if (e.key.length === 1 && e.key.match(/[a-z]/i)) {
            duckSequence += e.key.toLowerCase();
            
            // Keep only last 4 characters
            if (duckSequence.length > 4) {
                duckSequence = duckSequence.slice(-4);
            }
            
            // Check for "duck" sequence
            if (duckSequence === 'duck' && !gameActive) {
                startDuckGame();
                duckSequence = ''; // Reset sequence
            }
        }
    });

    function startDuckGame() {
        gameActive = true;
        missedDucks = 0;
        duckScore = 0;
        activeDucks.clear();
        
        // Show counter
        document.getElementById('duckCounter').style.display = 'block';
        document.getElementById('duckScore').textContent = '0';
        document.getElementById('gameOver').style.display = 'none';
        
        // Start spawning ducks
        duckInterval = setInterval(spawnDuck, 1200);
        
        // Auto-stop after 30 seconds
        setTimeout(stopDuckGame, 30000);
    }

    function spawnDuck() {
        if (!gameActive) return;
        
        const duck = document.createElement('div');
        duck.className = 'duck';
        duck.style.cssText = `
            position: fixed;
            top: -60px;
            left: ${Math.random() * (window.innerWidth - 60)}px;
            width: 60px;
            height: 60px;
            background-image: url('${duckSVG}');
            background-size: contain;
            background-repeat: no-repeat;
            cursor: pointer;
            z-index: 9998;
            transition: transform 0.3s, opacity 0.3s;
            pointer-events: auto;
        `;
        
        const duckId = Symbol('duck');
        activeDucks.add(duckId);
        
        duck.addEventListener('click', function() {
            // Duck hit animation
            this.style.transform = 'scale(1.5) rotate(360deg)';
            this.style.opacity = '0';
            
            // Add score
            duckScore++;
            document.getElementById('duckScore').textContent = duckScore;
            
            // Remove from active ducks
            activeDucks.delete(duckId);
            
            // Remove duck after animation
            setTimeout(() => {
                if (this.parentNode) {
                    this.parentNode.removeChild(this);
                }
            }, 300);
        });
        
        document.body.appendChild(duck);
        
        // Animate duck falling
        let position = -60;
        const speed = 2 + Math.random() * 2;
        
        function animate() {
            if (!gameActive || !document.body.contains(duck)) return;
            
            position += speed;
            duck.style.top = position + 'px';
            
            // Check if duck reached bottom (fully out of view)
            if (position > window.innerHeight + 60) {
                missedDucks++;
                activeDucks.delete(duckId);
                
                // Remove duck
                if (duck.parentNode) {
                    duck.parentNode.removeChild(duck);
                }
                
                // Check game over
                if (missedDucks >= 3) {
                    gameOver();
                }
            } else {
                requestAnimationFrame(animate);
            }
        }
        
        animate();
    }

    function gameOver() {
        stopDuckGame();
        document.getElementById('finalScore').textContent = duckScore;
        document.getElementById('gameOver').style.display = 'flex';
    }

    function stopDuckGame() {
        gameActive = false;
        clearInterval(duckInterval);
        
        // Remove all ducks
        document.querySelectorAll('.duck').forEach(duck => {
            if (duck.parentNode) {
                duck.parentNode.removeChild(duck);
            }
        });
        activeDucks.clear();
        
        // Hide counter if not game over
        if (missedDucks < 3) {
            setTimeout(() => {
                document.getElementById('duckCounter').style.display = 'none';
            }, 2000);
        }
    }

    function resetGame() {
        document.getElementById('gameOver').style.display = 'none';
        document.getElementById('duckCounter').style.display = 'none';
        stopDuckGame();
    }

    // Stop game when switching tabs or closing
    window.addEventListener('beforeunload', stopDuckGame);
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            stopDuckGame();
        }
    });
</script>

</body>
</html>'''