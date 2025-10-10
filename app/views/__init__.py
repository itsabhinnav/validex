"""
Views package for MVC architecture
"""

from .base_view import BaseView
from .dashboard_view import DashboardView
from .test_cases_view import TestCasesView
from .admin_view import AdminView
from .reports_view import ReportsView

__all__ = [
    'BaseView',
    'DashboardView',
    'TestCasesView', 
    'AdminView',
    'ReportsView'
]

