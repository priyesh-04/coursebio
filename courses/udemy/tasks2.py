"""
Udemy Test Course Importer

This module provides backward compatibility for existing imports.
For new code, use: from courses.udemy.test_importer import udemy_import_test_course
"""

from .test_importer import udemy_import_test_course, UdemyTestImporter

# Backward compatibility - expose the main function
udemy = udemy_import_test_course

# Expose the class for direct use
__all__ = ['udemy', 'udemy_import_test_course', 'UdemyTestImporter']
    