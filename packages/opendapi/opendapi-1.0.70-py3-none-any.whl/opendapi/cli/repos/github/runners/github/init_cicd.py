"""
CLI for initializing the server driven CICD writing the CICD ID to a file
for use by other commands for uploading files to the DAPI server
and starting the server driven CICD.

This command is invoked in a github CI runner for a github repo:
`opendapi github github init-cicd`
"""

# pylint: disable=duplicate-code

import click

from opendapi.cli.context_agnostic import cicd_init
from opendapi.cli.options import dapi_server_options, dev_options, opendapi_run_options
from opendapi.cli.repos.github.options import repo_options
from opendapi.cli.repos.github.runners.github.options import (
    construct_change_trigger_event,
    runner_options,
)
from opendapi.cli.utils import write_cicd_initialized_file


@click.command()
# common options
@dapi_server_options
@dev_options
@opendapi_run_options
# github repo options
@repo_options
# github repo github runner options
@runner_options
def cli(**kwargs):
    """
    CLI for initializing the server driven CICD writing the CICD ID to a file
    for use by other commands for uploading files to the DAPI server
    and starting the server driven CICD.

        This command is invoked in a github CI runner for a github repo:
        `opendapi github github init-cicd`
    """

    run_id = kwargs["github_run_id"]
    run_attempt = kwargs["github_run_attempt"]
    run_number = kwargs["github_run_number"]
    change_trigger_event = construct_change_trigger_event(kwargs)

    woven_cicd_id, _ = cicd_init(
        lambda dr: dr.cicd_init_github_github(
            run_id=run_id,
            run_attempt=run_attempt,
            run_number=run_number,
        ),
        change_trigger_event,
        kwargs,
    )
    write_cicd_initialized_file(
        {
            "woven_cicd_id": woven_cicd_id,
            "base_commit_sha": change_trigger_event.before_change_sha,
            "head_commit_sha": change_trigger_event.after_change_sha,
            "head_commit_sha_timestamp": change_trigger_event.after_change_sha_timestamp,
        }
    )
