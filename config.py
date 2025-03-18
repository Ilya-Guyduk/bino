"""
This module contains the configuration for the application, including
the current version and feature flags.

Attributes:
    VERSION (str): The current version of the application, following SemVer.
    FEATURE_FLAGS (dict): A dictionary containing feature flags for enabling or
                           disabling specific features in the application. For
                           example, "ENABLE_SQL_SUPPORT" controls the SQL support.
"""
VERSION = "v1.0.0"

FEATURE_FLAGS = {
    "ENABLE_SQL_SUPPORT": False
}
