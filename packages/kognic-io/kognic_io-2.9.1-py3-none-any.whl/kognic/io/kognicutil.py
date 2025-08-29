import os
from pprint import pprint
from typing import List

import click
from tabulate import tabulate

from kognic.io.client import KognicIOClient
from kognic.io.util import get_view_links

try:
    from kognic.io.tools.calibration.wasm_cli import cli as wasm_cli
except ImportError:
    print("WARNING: Wasm commands not available, install with `pip install kognic-io[wasm]` to enable them.")
    wasm_cli = click.Group(name="wasm")


def _tabulate(body, headers, title=None):
    tab = tabulate(
        body,
        headers=headers,
        tablefmt="fancy_grid",
    )
    if title:
        title_len = len(title)
        spacing = len(tab.split("\n")[0])

        roof = "=" * spacing
        floor = "=" * spacing

        left_multi = spacing // 2 - title_len // 2 - 1

        title_text_left = " " * left_multi + title
        title_text = title_text_left

        title_house = roof + "\n" + title_text + "\n" + floor
        tab = title_house + "\n" + tab
    return tab


def _get_table(sequence, headers, title=None):
    body = []
    for p in sequence:
        body.append([vars(p)[h] for h in headers])
    return _tabulate(body, headers, title)


@click.group()
@click.pass_context
def cli(ctx):
    """A CLI wrapper for Kognic utilities"""


@click.command()
@click.argument("project", nargs=1, default=None, required=False, type=str)
@click.option("--get-batches", is_flag=True)
@click.pass_obj
def projects(obj, project, get_batches):
    client = obj["client"]
    print()
    if project and get_batches:
        list_of_input_batches = client.project.get_project_batches(project)
        headers = ["created", "project", "batch", "title", "status", "updated"]
        tab = _get_table(list_of_input_batches, headers, "BATCHES")
        print(tab)
    elif project:
        list_of_projects = client.project.get_projects()
        target_project = [p for p in list_of_projects if p.project == project]
        headers = ["created", "project", "title", "description", "status"]
        tab = _get_table(target_project, headers, "PROJECTS")
        print(tab)
    else:
        list_of_projects = client.project.get_projects()
        headers = ["created", "project", "title", "description", "status"]
        tab = _get_table(list_of_projects, headers, "PROJECTS")
        print(tab)


@click.command()
@click.option("--project", nargs=1, default=None, required=False, type=str)
@click.option("--batch", nargs=1, default=None, required=False, type=str)
@click.option("--external-ids", required=False, multiple=True)
@click.option("--include-invalidated", required=False, is_flag=True)
@click.option("--view", is_flag=True)
@click.option("--uuids", type=str, help="Comma separated list of scene uuids")
@click.pass_obj
def inputs(obj, project, batch, external_ids, include_invalidated, view, uuids):
    client = obj["client"]
    print()
    if view and project:
        inputs = client.input.get_inputs(project, batch, external_ids=external_ids, include_invalidated=include_invalidated)
        view_dict = {input.scene_uuid: input.view_link for input in inputs}
        body = []
        headers = ["scene_uuid", "view_link"]
        for uuid, link in view_dict.items():
            body.append([uuid, link])
        tab = _tabulate(body, headers, title="VIEW LINKS FOR INPUTS")
        print(tab)
    elif uuids is not None:
        uuids = uuids.split(",")
        inputs = client.input.get_inputs_by_uuids(uuids)
        headers = ["scene_uuid", "external_id", "batch", "scene_type", "status", "view_link", "error_message"]
        tab = _get_table(inputs, headers, "INPUTS")
        print(tab)
    else:
        inputs = client.input.get_inputs(project, batch, include_invalidated=include_invalidated)
        headers = ["scene_uuid", "external_id", "batch", "scene_type", "status", "view_link", "error_message"]
        tab = _get_table(inputs, headers, "INPUTS")
        print(tab)


@click.command()
@click.argument("uuids", nargs=-1, type=str)
@click.option("--view", is_flag=True, help="Reduce output to view links only")
@click.option("--status", is_flag=True, help="Reduce output to status only")
@click.pass_obj
def scenes(obj, uuids: List[str], view: bool, status: bool):
    client = obj["client"]
    if not uuids:
        raise click.BadParameter("Please provide at least one scene uuid.")
    if view and status:
        raise click.BadParameter("Please provide either --view or --status, not both.")

    print()
    scenes = client.scene.get_scenes_by_uuids(uuids)
    if view:
        body = [[s.uuid, s.view_link] for s in scenes]
        headers = ["uuid", "view_link"]
        tab = _tabulate(body, headers, title="VIEW LINKS FOR SCENES")
        print(tab)
    elif status:
        body = [(s.uuid, s.status, s.error_message) for s in scenes]
        headers = ["uuid", "status", "error_message"]
        tab = _tabulate(body, headers, title="STATUS FOR SCENES")
        print(tab)
    else:
        headers = ["uuid", "external_id", "scene_type", "status", "view_link", "error_message"]
        tab = _get_table(scenes, headers=headers, title="SCENES")
        print(tab)


@click.command()
@click.argument("input_uuid", nargs=1, required=True, type=str)
@click.pass_obj
def view(obj, input_uuid):
    print()
    view_dict = get_view_links([input_uuid])
    body = [[input_uuid, view_dict[input_uuid]]]
    headers = ["uuid", "view_link"]
    tab = _tabulate(body, headers, title="VIEW LINK")
    print(tab)


@click.command()
@click.option("--id", nargs=1, default=None, required=False, type=str)
@click.option("--external-id", nargs=1, required=False, type=str)
@click.option("--raw", is_flag=True)
@click.pass_obj
def calibration(obj, id, external_id, raw):
    client = obj["client"]
    print()
    if id is not None:
        calibration_entry = client.calibration.get_calibration(id)
        headers = ["id", "external_id", "created"]
        tab = _get_table([calibration_entry], headers, "CALIBRATION")
        print(tab)
        if raw:
            print()
            pprint(calibration_entry.calibration)
    elif external_id is not None:
        list_of_calibrations = client.calibration.get_calibrations(external_id=external_id)
        headers = ["id", "external_id", "created"]
        tab = _get_table(list_of_calibrations, headers, "CALIBRATION")
        print(tab)
    else:
        list_of_calibrations = client.calibration.get_calibrations()
        headers = ["id", "external_id", "created"]
        tab = _get_table(list_of_calibrations, headers, "CALIBRATION")
        print(tab)


cli.add_command(projects)
cli.add_command(inputs)
cli.add_command(scenes)
cli.add_command(calibration)
cli.add_command(view)

cli.add_command(wasm_cli)


def main():
    env = os.getenv("KOGNIC_CLIENT_ORGANIZATION_ID", None)
    if env:
        org_id = int(env)
        print("<" * 25, f" Acting on behalf of organization {org_id}", 25 * ">")
    else:
        org_id = None

    client = KognicIOClient(auth=None, client_organization_id=org_id)

    cli(obj={"client": client}, prog_name="kognicutil")
