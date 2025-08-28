==================
**azdo_pipeline**
==================

Overview
--------

A Python module to call Azure DevOps pipeline and optionally search output.

Prerequisites
-------------

- Python 3.9 or higher.
- Azure DevOps PAT (Personal Access Token) with Builds (read and execute) permissions.

Usage
-----

Installation:

.. code-block:: BASH

   pip3 install azdo_pipeline
   # or
   python3 -m pip install azdo_pipeline

Bash:

.. code-block:: BASH

   call_azdo_pipeline \
      -t "<pat>" \
      -o "<org>" \
      -p "<project_id>" \
      -l <pipeline_id> \
      [-d '<run_parameters>' \]
      [-r <run_id> \]
      [-g <log_id> \]
      [-s "<search_pattern>"]

Example:

.. code-block:: BASH

   call_azdo_pipeline \
      -t "sd354sd36f5sf4s6v4s" \
      -o "my-org" \
      -p "asfj-349859njnkfv-dvdf-3rfsw" \
      -l 35 \
      -d '{"templateParameters": {"agentPool": "ubuntu-latest"}}' \
      -r 3210 \
      -g 6 \
      -s ".*SUCCESSFUL.*"

   Retrieving pipeline run logs list...
   Retrieving pipeline run log 9...
   Extracting output from logs...
   { 'data': '2025-08-23T08:07:29.0226728Z SUCCESSFUL',
      'run_id': 3210,
      'status': 200}

Arguments
---------

- -t PAT (Personal Access Token) for Azure DevOps authentication.
- -o Organization name in Azure DevOps.
- -p Project ID or name in Azure DevOps.
- -l Pipeline ID in Azure DevOps.
- -d (Optional) JSON string with run parameters.
- -r (Optional) Specific run ID to fetch logs from.
- -g (Optional) Specific log ID to fetch.
- -s (Optional) Regex pattern to search for in the logs.

Return Value
------------

A dictionary with the following keys:

- data: The matched log line or an empty string if no match is found.
- run_id: The ID of the pipeline run.
- status: The HTTP status code of the API response.
