"""
osintbuddy.utils.
================

Utilities package for osintbuddy.

Provides:

- Generic text and data transformation helpers
- Selenium WebDriver context management

Modules
-------
generic
    Core functions: MAP_KEY, chunks, find_emails, to_clean_domain,
    slugify, to_camel_case, to_snake_case, dkeys_to_snake_case.
deps
    Dependency utilities: get_driver context manager.

Re-exports
----------
MAP_KEY
chunks
find_emails
to_clean_domain
slugify
to_camel_case
to_snake_case
dkeys_to_snake_case
get_driver
"""

import osintbuddy.utils.deps as deps
import osintbuddy.utils.generic as generic

# Generic utilities
MAP_KEY = generic.MAP_KEY
chunks = generic.chunks
find_emails = generic.find_emails
to_clean_domain = generic.to_clean_domain
slugify = generic.slugify
to_camel_case = generic.to_camel_case
to_snake_case = generic.to_snake_case
dkeys_to_snake_case = generic.dkeys_to_snake_case

# Dependency utilities
get_driver = deps.get_driver

__all__ = [
    "MAP_KEY",
    "chunks",
    "find_emails",
    "to_clean_domain",
    "slugify",
    "to_camel_case",
    "to_snake_case",
    "dkeys_to_snake_case",
    "get_driver",
]
