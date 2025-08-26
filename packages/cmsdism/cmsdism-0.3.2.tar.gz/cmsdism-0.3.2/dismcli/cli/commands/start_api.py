import click

from ...lib.start_api.start_api import InferenceServiceLocalApi


@click.command()
@click.option("-r", "--resource", help="Inference service resource name.")
@click.option("-cr", "--container-runtime", default=None, help="Container runtime.")
def start_api_command(resource, container_runtime):
    api = InferenceServiceLocalApi(resource, container_runtime)
    api.start()
