"""
Udemy Course Import Module

This module provides functionality for importing courses from Udemy API.
It includes both production and test importers with shared base functionality.
"""

# Udemy imports
from .base import UdemyImportBase, BASE_CATEGORY_MAPPING, PRODUCTION_CATEGORY_MAPPING
from .importer import UdemyProductionImporter, udemy_import_courses
from .test_importer import UdemyTestImporter, udemy_import_test_course

# Backward compatibility imports
from .tasks import udemy as production_udemy, udemy_import_courses as udemy_import_courses_compat, UdemyProductionImporter as UdemyProductionImporterCompat
from .tasks2 import udemy as test_udemy, udemy_import_test_course as udemy_import_test_course_compat, UdemyTestImporter as UdemyTestImporterCompat

__all__ = [
    'UdemyImportBase',
    'BASE_CATEGORY_MAPPING',
    'PRODUCTION_CATEGORY_MAPPING',
    'UdemyProductionImporter',
    'udemy_import_courses',
    'UdemyTestImporter',
    'udemy_import_test_course',
    # Backward compatibility
    'production_udemy',
    'test_udemy',
    'udemy_import_courses_compat',
    'udemy_import_test_course_compat',
    'UdemyProductionImporterCompat',
    'UdemyTestImporterCompat',
]
