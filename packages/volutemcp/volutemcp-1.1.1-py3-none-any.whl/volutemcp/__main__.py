#!/usr/bin/env python3
"""
VoluteMCP package main entry point.
Allows running: python -m volutemcp.server_local
"""

import sys
from .server_local import main

if __name__ == "__main__":
    main()
