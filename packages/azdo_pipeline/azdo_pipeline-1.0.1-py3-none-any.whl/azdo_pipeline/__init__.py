#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""
Call Azure DevOps pipeline and optionally search output.

Prerequisites:
    - Azure DevOps Personal Access Token (PAT)

PAT Permissions:
    - Builds (read and execute)

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

from typing import Union
from pprint import pprint
import sys
import base64
import json
import re
import time
import argparse
import urllib3


__version__ = "1.0.1"
__author__ = "Ahmad Ferdaus Abd Razak"
__application__ = "call_azdo_pipeline"


def encode_base64(
    data: str
) -> str:
    """Encode data to Base64."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return base64.b64encode(data).decode("utf-8")


def search_output(
    log_contents: list,
    search_pattern: str
) -> str:
    """Extract output from log contents."""
    pattern = rf"{search_pattern}"
    output = "\n".join([line for line in log_contents if re.search(pattern, line)])
    return output


def init_http(
    host: str
) -> urllib3.PoolManager:
    """Initialize HTTP connection."""
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\$", host):
        http = urllib3.PoolManager(
            cert_reqs='CERT_NONE',
            assert_hostname=False
        )
    else:
        http = urllib3.PoolManager()
    return http


def http_get(
    http: urllib3.PoolManager,
    url: str,
    token: str,
    headers: dict
) -> dict:
    """Send HTTP GET request."""
    std_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Basic {token}"
    }
    headers = {**std_headers, **headers}
    response = http.request("GET", url, headers=headers)
    return {
        "status": response.status,
        "data": json.loads(response.data.decode("utf-8"))
    }


def http_post(
    http: urllib3.PoolManager,
    url: str,
    token: str,
    headers: dict,
    body: dict
) -> dict:
    """Send HTTP POST request."""
    std_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Basic {token}"
    }
    headers = {**std_headers, **headers}
    if body == {}:
        response = http.request("POST", url, headers=headers)
    else:
        response = http.request("POST", url, headers=headers, body=json.dumps(body))
    return {
        "status": response.status,
        "data": json.loads(response.data.decode("utf-8"))
    }


def call_pipeline(
    pat: str,
    org: str,
    project_id: str,
    pipeline_id: int,
    run_parameters: Union[str, None],
    run_id: Union[int, None],
    log_id: Union[int, None],
    search_pattern: Union[str, None]
) -> dict:
    """Call Azure DevOps pipeline and optionally search output."""
    # Initialize HTTP connection.
    host = f"dev.azure.com/{org}"
    http = init_http(host)
    token = encode_base64(f":{pat}")

    # If run_id is provided, skip creating new run and check existing run.
    run_state = "inProgress"
    if run_id is None:

        # Create new pipeline run.
        create_endpoint = (
            f"{project_id}/_apis"
            f"/pipelines/{pipeline_id}/runs?api-version=7.1"
        )
        print("Creating new pipeline run...")
        response = http_post(
            http,
            f"https://{host}/{create_endpoint}",
            token,
            {},
            json.loads(run_parameters) if run_parameters is not None else {}
        )

        # Continue if previous step was successful.
        if response["status"] == 200:
            run_id = response["data"]["id"]
            state = response["data"]["state"]

            # Wait for pipeline run to complete.
            print("Waiting for pipeline run to complete...")
            while state == "inProgress":
                runs_endpoint = (
                    f"{project_id}/_apis"
                    f"/pipelines/{pipeline_id}/runs/{run_id}?api-version=7.1"
                )
                print("Checking pipeline run status...")
                response = http_get(http, f"https://{host}/{runs_endpoint}", token, {})

                # Continue if previous step was successful.
                if response["status"] == 200:
                    state = response["data"]["state"]
                    time.sleep(1)
                else:
                    print(f"{response['status']}. Pipeline run status check failed: {response['data']}")
                    sys.exit(1)

            # Get final run state and result.
            run_state = response.get("data", {}).get("state", None)
            run_result = response.get("data", {}).get("result", None)
            run_id = response.get("data", {}).get("id", None)
            status = response["status"]
            data = f"Pipeline run completed with state: {run_state}, result: {run_result}"

        else:
            run_id = None
            status = response["status"]
            data = f"Pipeline run creation failed: {response['data']}"

    # If run ID or search pattern is provided, retrieve logs and extract output.
    if (
        run_state == "completed"
        and search_pattern is not None
        or run_id is not None
        and search_pattern is not None
    ):
        list_endpoint = (
            f"{project_id}/_apis"
            f"/pipelines/{pipeline_id}/runs/{run_id}/logs?api-version=7.1"
        )
        print("Retrieving pipeline run logs list...")

        # Get list of logs if log_id is not provided.
        if log_id is None:
            response = http_get(http, f"https://{host}/{list_endpoint}", token, {})

            # Continue if previous step was successful.
            if response["status"] == 200:
                log_ids = [[log["id"] for log in response["data"]["logs"]][-1]]

            else:
                print(
                    f"{response['status']}."
                    " Pipeline run logs list retrieval failed:"
                    f" {response['data']}"
                )
                sys.exit(1)

        else:
            log_ids = [log_id]

        # Retrieve log contents.
        log_contents = []
        for id in log_ids:

            logs_endpoint = (
                f"{project_id}/_apis"
                f"/build/builds/{run_id}/logs/{id}?api-version=7.1"
            )
            print(f"Retrieving pipeline run log {id}...")
            response = http_get(http, f"https://{host}/{logs_endpoint}", token, {})
            log_contents.extend(response["data"]["value"])

        # Extract output from log contents.
        print("Extracting output from logs...")
        output = search_output(log_contents, search_pattern)
        status = 200
        data = output

        # Return results with search pattern.
        return_body = {
            "run_id": run_id,
            "status": status,
            "data": data
        }

    # Handle cases where search_pattern is missing.
    elif run_id is not None and search_pattern is None:
        return_body = {
            "run_id": run_id,
            "status": 400,
            "data": "Both run_id and search_pattern must be provided to retrieve logs."
        }

    # Return results without search pattern.
    else:
        return_body = {
            "run_id": run_id,
            "status": status,
            "data": data
        }

    return return_body


def get_params():
    """Get parameters from script inputs."""
    myparser = argparse.ArgumentParser(
        add_help=True,
        allow_abbrev=False,
        description="Call Azure DevOps pipeline and optionally search output.",
        usage=f"{__application__} [options]"
    )
    myparser.add_argument(
        "-V", "--version", action="version", version=f"{__application__} {__version__}"
    )
    myparser.add_argument(
        "-t",
        "--pat",
        action="store",
        help="Azure DevOps Personal Access Token (PAT).",
        nargs="?",
        required=True,
        type=str
    )
    myparser.add_argument(
        "-o",
        "--org",
        action="store",
        help="Azure DevOps organization name.",
        nargs="?",
        required=True,
        type=str
    )
    myparser.add_argument(
        "-p",
        "--project_id",
        action="store",
        help="Azure DevOps project ID or name.",
        nargs="?",
        required=True,
        type=str
    )
    myparser.add_argument(
        "-l",
        "--pipeline_id",
        action="store",
        help="Azure DevOps pipeline ID.",
        nargs="?",
        required=True,
        type=int
    )
    myparser.add_argument(
        "-d",
        "--run_parameters",
        action="store",
        help="JSON string of parameters to pass to the pipeline run. Default: None.",
        nargs="?",
        default=None,
        required=False,
        type=str
    )
    myparser.add_argument(
        "-r",
        "--run_id",
        action="store",
        help="Azure DevOps pipeline run ID. Default: None.",
        nargs="?",
        default=None,
        required=False,
        type=int
    )
    myparser.add_argument(
        "-g",
        "--log_id",
        action="store",
        help="Azure DevOps pipeline log ID. Default: None.",
        nargs="?",
        default=None,
        required=False,
        type=int
    )
    myparser.add_argument(
        "-s",
        "--search_pattern",
        action="store",
        help="Regex pattern to search in logs. Default: None.",
        nargs="?",
        default=None,
        required=False,
        type=str
    )
    return myparser.parse_args()


def main():
    """Execute main function."""
    args = get_params()
    response = call_pipeline(
        args.pat,
        args.org,
        args.project_id,
        args.pipeline_id,
        args.run_parameters,
        args.run_id,
        args.log_id,
        args.search_pattern
    )
    pprint(response, indent=2)
