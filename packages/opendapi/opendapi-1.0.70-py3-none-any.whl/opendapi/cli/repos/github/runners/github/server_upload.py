"""
CLI for loading the base and head collected dapi file information,
analyzing them, uploading the required information to the DAPI server

This command is invoked in a buildkite CI runner for a github repo and a single runtime:
`opendapi github buildkite server-upload`
"""

# pylint: disable=duplicate-code

import click

from opendapi.adapters.dapi_server import CICDIntegration
from opendapi.cli.common import get_opendapi_config_from_root
from opendapi.cli.context_agnostic import (
    cicd_get_s3_upload_data,
    cicd_persist_files,
    load_collected_files,
)
from opendapi.cli.options import (
    cicd_param_options,
    dapi_server_options,
    dbt_options,
    dev_options,
    git_options,
    opendapi_run_options,
    runtime_options,
)
from opendapi.cli.repos.github.options import repo_options
from opendapi.cli.repos.github.runners.github.options import (
    construct_change_trigger_event,
    runner_options,
)
from opendapi.defs import CommitType


@click.command()
# common options
@dapi_server_options
@dbt_options
@dev_options
@git_options
@opendapi_run_options
@runtime_options
@cicd_param_options
# github repo options
@repo_options
# github repo github runner options
@runner_options
def cli(**kwargs):
    """
    CLI for loading the base and head collected dapi file information,
    analyzing them, uploading the required information to the DAPI server

        This command is invoked in a github CI runner for a github repo and a single runtime:
        `opendapi github github server-upload`
    """

    woven_cicd_id = kwargs["woven_cicd_id"]
    runtime = kwargs["runtime"]
    change_trigger_event = construct_change_trigger_event(kwargs)
    opendapi_config = get_opendapi_config_from_root(
        local_spec_path=kwargs.get("local_spec_path"),
        validate_config=True,
    )
    opendapi_config.assert_runtime_exists(runtime)

    base_collected_files = load_collected_files(
        opendapi_config,
        CommitType.BASE,
        runtime,
    )
    head_collected_files = load_collected_files(
        opendapi_config,
        CommitType.HEAD,
        runtime,
    )

    s3_upload_data = cicd_get_s3_upload_data(
        woven_cicd_id,
        CICDIntegration.GITHUB_GITHUB,
        change_trigger_event,
        kwargs,
    )
    cicd_persist_files(
        base_collected_files,
        head_collected_files,
        change_trigger_event,
        opendapi_config,
        s3_upload_data,
        runtime,
        kwargs,
    )
