#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""
Call Azure DevOps pipeline and optionally search output.

Prerequisites:
    - Azure DevOps Personal Access Token (PAT)

PAT Permissions:
    - Build (read and execute)

Usage:
    call_azdo_pipeline \\
        -t <pat> \\
        -o <org> \\
        -p <project_id> \\
        -l <pipeline_id> \\
        [-d <run_parameters> \\]
        [-r <run_id> \\]
        [-g <log_id> \\]
        [-s <search_pattern>]

Returns:
    Object with run ID, status code, and data.
"""

import __init__

if __name__ == "__main__":
    __init__.main()
