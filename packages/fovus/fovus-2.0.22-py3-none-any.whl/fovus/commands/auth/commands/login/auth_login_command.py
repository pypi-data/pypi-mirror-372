from typing import Union

import click

from fovus.adapter.fovus_sign_in_adapter import FovusSignInAdapter
from fovus.config.config import Config


@click.option(
    "--gov",
    "-g",
    is_flag=True,
    type=bool,
    help="Login to Fovus Gov Cloud.",
)
@click.option("--email", "-e", type=str, help="Email address")
@click.option("--password", "-p", type=str,
              help="Personal access token (PAT). Your PAT can be found under your user settings at https://app.fovus.co/user/settings/authentication")
@click.command("login")
def auth_login_command(gov: bool, email: Union[str, None], password: Union[str, None]):
    """Login through the Fovus web app."""
    if gov:
        Config.set_is_gov(True)
    else:
        Config.set_is_gov(False)

    fovus_sign_in_adapter = FovusSignInAdapter(is_gov=gov)
    fovus_sign_in_adapter.sign_in_concurrent(email=email, password=password)
