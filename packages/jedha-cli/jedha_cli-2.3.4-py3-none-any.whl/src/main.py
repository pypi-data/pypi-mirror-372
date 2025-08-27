#! /usr/bin/python3

import os
import subprocess
from typing import Annotated, List, Optional

import typer
from rich import print
from rich.console import Console
from rich.table import Table
from yaml import safe_load

from .misc import (check_for_updates, cleanup_lab, get_docker_compose_command,
                   get_lab_config_file, get_lab_folder_name, get_running_labs,
                   get_yaml_labs, is_docker_running, is_lab_already_running)

app = typer.Typer(
    name="jedhacli",
    help="""
A CLI to manage the labs for Cybersecurity Bootcamp at Jedha (https://jedha.co).

⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n
⠀⠀⠀⠀⣠⣧⠷⠆⠀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀\n
⠀⠀⣐⣢⣤⢖⠒⠪⣭⣶⣿⣦⠀⠀⠀⠀⠀⠀⠀\n
⠀⢸⣿⣿⣿⣌⠀⢀⣿⠁⢹⣿⡇⠀⠀⠀⠀⠀⠀\n
⠀⢸⣿⣿⣿⣿⣿⡿⠿⢖⡪⠅⢂⠀⠀⠀⠀⠀⠀\n
⠀⠀⢀⣔⣒⣒⣂⣈⣉⣄⠀⠺⣿⠿⣦⡀⠀⠀⠀\n
⠀⡴⠛⣉⣀⡈⠙⠻⣿⣿⣷⣦⣄⠀⠛⠻⠦⠀⠀\n
⡸⠁⢾⣿⣿⣁⣤⡀⠹⣿⣿⣿⣿⣿⣷⣶⣶⣤⠀\n
⡇⣷⣿⣿⣿⣿⣿⡇⠀⣿⣿⣿⣿⣿⣿⡿⠿⣿⡀\n
⡇⢿⣿⣿⣿⣟⠛⠃⠀⣿⣿⣿⡿⠋⠁⣀⣀⡀⠃\n
⢻⡌⠀⠿⠿⠿⠃⠀⣼⣿⣿⠟⠀⣠⣄⣿⣿⡣⠀\n
⠈⢿⣶⣤⣤⣤⣴⣾⣿⣿⡏⠀⣼⣿⣿⣿⡿⠁⠀\n
⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⠀⠀⣩⣿⡿⠋⠀⠀⠀\n
⠀⠀⠀⠀⠈⠙⠛⠿⠿⠿⠇⠀⠉⠁⠀⠀⠀⠀⠀\n
    """,
    epilog="Made with ❤️ by the Jedha Bootcamp Team",
    no_args_is_help=True,
)

console = Console()


# @app.command("config", help="Configure the CLI.")
# def config():
#     """
#     Configure the CLI by prompting the user for the required information.
#     """
#     pass


@app.command("list", help="List all the labs available.")
def list():
    """
    List all the labs available.
    """
    filename_array = get_yaml_labs()
    table = Table("Name", "IP", "Description", show_lines=True, title="Available Labs")
    for i in filename_array:
        table.add_row(i["name"], i["ip"], i["description"])
    console.print(table)


@app.command("dl", help="Download (but not start) one or more lab(s) environment.")
def download(labnames: List[str]):
    """
    Download a lab.

    Args:
        labnames (List[str]): List of the lab names.
    """
    if not is_docker_running():
        print("Docker is not running. Please start Docker and try again.")
        raise typer.Exit(1)

    for labname in labnames:
        actual_labname = get_lab_folder_name(labname)

        lab_config_file_path = get_lab_config_file(actual_labname)
        if not lab_config_file_path or not os.path.exists(lab_config_file_path):
            print(f"Are you sure about the lab name? We don't know any {labname}... 🤔")
            return

        try:
            command = get_docker_compose_command(["--file", lab_config_file_path, "pull"])
            subprocess.run(
                command,
                check=True,
            )
            print(f"Lab {labname} downloaded successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to download lab {labname}.")


@app.command(
    "status",
    help="Show the running labs. If a lab name is provided, it will show the status of that lab.",
)
def status(labname: Annotated[Optional[str], typer.Argument()] = None):
    """
    Show the list of running labs.

    If a lab name is provided, it will show the status of that lab.

    Args:
        labname (Optional[str]): Name of the lab.
    """
    if not is_docker_running():
        print("Docker is not running. Please start Docker and try again.")
        raise typer.Exit(1)

    if labname is None:
        running_labs = get_running_labs()
        if running_labs:
            print(
                f"🔍 You have the following running labs: [b]{', '.join(running_labs)}[/b]."
            )
        else:
            print("☕️ No labs are currently running.")
        return

    actual_labname = get_lab_folder_name(labname)

    lab_config_file_path = get_lab_config_file(actual_labname)
    if not lab_config_file_path or not os.path.exists(lab_config_file_path):
        print(f"Are you sure about the lab name? We don't know any {labname}... 🤔")
        return

    with open(lab_config_file_path, "r") as file:
        docker_compose = safe_load(file)
    expected_containers = set(docker_compose["services"].keys())

    try:
        command = get_docker_compose_command(
            ["--file", lab_config_file_path, "-p", labname, "ps"]
        )
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        lines = result.stdout.splitlines()
        container_lines = lines[1:]
        running_containers = set(
            line.split()[0] for line in container_lines if "Up" in line
        )

        if not running_containers:
            print(f"😴 {labname} is not running")
        elif running_containers == expected_containers:
            print(f"✅ {labname} is running as expected")
        else:
            failed_containers = expected_containers - running_containers
            print(
                f"⛔️ Some issues with the following containers: {', '.join(failed_containers)}"
            )

    except subprocess.CalledProcessError as e:
        print(f"Failed to show status of lab {labname}. Is Docker running?")


@app.command("start", help="Start a specific lab environment.")
def start(labname: str):
    """
    Start a lab.

    Args:
        labname (str): Name of the lab.
    """
    if not is_docker_running():
        print("Docker is not running. Please start Docker and try again.")
        raise typer.Exit(1)
    
    actual_labname = get_lab_folder_name(labname)

    lab_config_file_path = get_lab_config_file(actual_labname)
    if not lab_config_file_path or not os.path.exists(lab_config_file_path):
        print(f"Are you sure about the lab name? We don't know any {labname}... 🤔")
        return

    if is_lab_already_running():
        return

    cleanup_lab(labname, lab_config_file_path)

    try:
        command = get_docker_compose_command(
            ["--file", lab_config_file_path, "-p", labname, "up", "-d"]
        )
        subprocess.run(
            command,
            check=True,
        )
        print(f"Lab {labname} started successfully.")
    except subprocess.CalledProcessError as e:
        print(
            f"Failed to start lab {labname}: Error with the docker compose file or Docker itself"
        )


@app.command("restart", help="Restart a lab.")
def restart(labname: str):
    """
    Restart a lab.

    Args:
        labname (str): Name of the lab.
    """
    if not is_docker_running():
        print("Docker is not running. Please start Docker and try again.")
        raise typer.Exit(1)

    actual_labname = get_lab_folder_name(labname)

    lab_config_file_path = get_lab_config_file(actual_labname)
    if not lab_config_file_path or not os.path.exists(lab_config_file_path):
        print(f"Are you sure about the lab name? We don't know any {labname}... 🤔")
        return

    cleanup_lab(labname, lab_config_file_path)

    try:
        command = get_docker_compose_command(
            ["--file", lab_config_file_path, "-p", labname, "restart"]
        )
        subprocess.run(
            command,
            check=True,
        )
        print(f"Lab {labname} restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(
            f"Failed to restart lab {labname}: Error with the docker compose file or Docker itself"
        )


@app.command("stop", help="Stop and clean up a specific lab environment.")
def stop(
    labname: str,
    force: Annotated[
        bool, typer.Option(prompt="Are you sure you want to stop the lab?")
    ],
):
    """
    Stop and clean up a specific lab environment.

    Args:
        labname (str): Name of the lab.
    """
    if not is_docker_running():
        print("Docker is not running. Please start Docker and try again.")
        raise typer.Exit(1)

    actual_labname = get_lab_folder_name(labname)

    lab_config_file_path = get_lab_config_file(actual_labname)
    if not lab_config_file_path or not os.path.exists(lab_config_file_path):
        print(f"Are you sure about the lab name? We don't know any {labname}... 🤔")
        return

    if force:
        try:
            command = get_docker_compose_command(
                [
                    "-p",
                    labname,
                    "--file",
                    lab_config_file_path,
                    "down",
                    "--remove-orphans",
                    "--volumes",
                ],
            )
            subprocess.run(
                command,
                check=True,
            )
            print(f"Lab {labname} taken down successfully.")
        except subprocess.CalledProcessError as e:
            print(
                f"Failed to take down lab {labname}: Error with the docker compose file or Docker itself"
            )
    else:
        print("Aborting.")


@app.command(
    "remove",
    help="Remove definitively a specific lab environment. Do it to free your disk space.",
)
def remove(
    labname: str,
    force: Annotated[
        bool, typer.Option(prompt="Are you sure you want to remove the lab?")
    ],
):
    """
    Remove a lab.

    Args:
        labname (str): Name of the lab.
    """
    if not is_docker_running():
        print("Docker is not running. Please start Docker and try again.")
        raise typer.Exit(1)

    actual_labname = get_lab_folder_name(labname)

    lab_config_file_path = get_lab_config_file(actual_labname)
    if not lab_config_file_path or not os.path.exists(lab_config_file_path):
        print(f"Are you sure about the lab name? We don't know any {labname}... 🤔")
        return

    if force:
        try:
            command = get_docker_compose_command(
                [
                    "-p",
                    labname,
                    "--file",
                    lab_config_file_path,
                    "down",
                    "--remove-orphans",
                    "--volumes",
                    "--rmi",
                    "all",
                ]
            )
            subprocess.run(
                command,
                check=True,
            )
            print(f"Lab {labname} definitively removed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to clean lab {labname}.")
    else:
        print("Aborting.")


def main():
    check_for_updates()
    app()


if __name__ == "__main__":
    main()
