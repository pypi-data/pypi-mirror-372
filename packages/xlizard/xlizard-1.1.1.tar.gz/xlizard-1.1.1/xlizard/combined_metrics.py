# -*- coding: utf-8 -*-
"""
Module for combining xlizard and SourceMonitor metrics
"""
from typing import Dict, List, Optional

class CombinedMetrics:
    def __init__(self, xlizard_data, sm_metrics: Optional[Dict] = None):
        self.xlizard = xlizard_data
        self.sourcemonitor = sm_metrics or {
            'comment_percentage': 0,
            'max_block_depth': 0,
            'pointer_operations': 0,
            'preprocessor_directives': 0
        }
        
    @property
    def filename(self):
        return self.xlizard.filename
        
    @property
    def functions(self):
        return self.xlizard.function_list
        
    @property
    def basename(self):
        return self.xlizard.filename.split('/')[-1]
        
    @property
    def dirname(self):
        dirs = self.xlizard.filename.split('/')[:-1]
        return '/'.join(dirs) if dirs else "Project Files"