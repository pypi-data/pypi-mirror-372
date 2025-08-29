import json

import click
from click.core import Context as ClickContext
from pydantic import ValidationError

from gable.api.client import GableAPIClient
from gable.cli.helpers.s3 import start_sca_run, upload_sca_results
from gable.cli.options import global_options
from gable.common_types import LineageDataFile


@click.command(
    add_help_option=False,
    name="upload",
    epilog="""Example:
    gable lineage upload --project-root ./path/to/project""",
)
@global_options(add_endpoint_options=False)
@click.option(
    "--project-root",
    help="The root directory of the project that will be analyzed.",
    type=click.Path(exists=True),
    required=True,
)
@click.option(
    "--results-file",
    help="The path to the results file.",
    type=click.Path(exists=True),
    required=True,
)
@click.pass_context
def lineage_upload(
    ctx: ClickContext,
    project_root: str,
    results_file: str,
):
    """
    Upload lineage data to Gable.
    """
    client: GableAPIClient = ctx.obj.client
    with open(results_file, "r") as f:
        results = json.load(f)
    try:
        lineageDataFile = LineageDataFile.model_validate(results)
    except ValidationError as e:
        raise click.ClickException(f"Invalid results file: {e}")

    run_id, presigned_url = start_sca_run(
        client,
        project_root,
        "upload",
        None,
        None,
        lineageDataFile.external_component_id,
    )
    upload_sca_results(run_id, presigned_url, lineageDataFile)
    click.echo(
        f"Uploaded lineage data from {results_file} to Gable with run ID: {run_id}"
    )
