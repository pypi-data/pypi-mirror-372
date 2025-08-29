"""
CLI for starting the server driven CICD after all
necessary files have been uploaded to the DAPI server.

This command is invoked in a buildkite CI runner for a github repo:
`opendapi github buildkite start-cicd`
"""

# pylint: disable=duplicate-code

import click

from opendapi.adapters.dapi_server import CICDIntegration
from opendapi.cli.common import get_opendapi_config_from_root
from opendapi.cli.context_agnostic import cicd_start
from opendapi.cli.options import (
    cicd_param_options,
    dapi_server_options,
    dev_options,
    git_options,
    opendapi_run_options,
)
from opendapi.cli.repos.github.options import repo_options
from opendapi.cli.repos.github.runners.buildkite.options import (
    construct_change_trigger_event,
    runner_options,
)


@click.command()
# common options
@dapi_server_options
@dev_options
@opendapi_run_options
@cicd_param_options
@git_options
# github repo options
@repo_options
# github repo github bk options
@runner_options
def cli(**kwargs):
    """
    CLI for starting the server driven CICD after all
    necessary files have been uploaded to the DAPI server.

    This command is invoked in a buildkite CI runner for a github repo:
    `opendapi github buildkite start-cicd`
    """

    woven_cicd_id = kwargs["woven_cicd_id"]
    change_trigger_event = construct_change_trigger_event(kwargs)
    opendapi_config = get_opendapi_config_from_root(
        local_spec_path=kwargs.get("local_spec_path"),
        validate_config=True,
    )

    job_id = kwargs["buildkite_job_id"]
    build_id = kwargs["buildkite_build_id"]
    retry_count = kwargs["buildkite_retry_count"]
    cicd_start(
        woven_cicd_id,
        opendapi_config,
        change_trigger_event,
        CICDIntegration.GITHUB_BUILDKITE,
        {
            "job_id": job_id,
            "build_id": build_id,
            "retry_count": retry_count,
        },
        kwargs,
    )
