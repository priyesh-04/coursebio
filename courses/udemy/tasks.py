"""
Udemy Production Course Importer

This module provides backward compatibility for existing imports.
For new code, use: from courses.udemy.importer import udemy_import_courses
"""

from .importer import udemy_import_courses, UdemyProductionImporter

# Backward compatibility - expose the main function
udemy = udemy_import_courses

# Expose the class for direct use
__all__ = ['udemy', 'udemy_import_courses', 'UdemyProductionImporter']
    