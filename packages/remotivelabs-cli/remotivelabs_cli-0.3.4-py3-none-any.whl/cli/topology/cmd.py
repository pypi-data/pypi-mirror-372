from __future__ import annotations

import typer

from cli.topology.start_trial import (
    MissingOrganizationError,
    NoActiveAccountError,
    NoOrganizationOrPermissionError,
    NotAuthorizedError,
    NotAuthorizedToStartTrialError,
    NotSignedInError,
    SubscriptionExpiredError,
    get_organization_and_account,
    start_trial,
)
from cli.typer import typer_utils
from cli.utils.console import print_generic_error, print_generic_message, print_hint

HELP = """
Manage RemotiveTopology resources
"""

app = typer_utils.create_typer(rich_markup_mode="rich", help=HELP)


@app.command("start-trial")
def start_trial_cmd(  # noqa: C901
    organization: str = typer.Option(None, help="Organization to start trial for", envvar="REMOTIVE_CLOUD_ORGANIZATION"),
) -> None:
    """
    Allows you ta start a 30 day trial subscription for running RemotiveTopology.

    You can read more at https://docs.remotivelabs.com/docs/remotive-topology.
    """

    try:
        (valid_organization, _) = get_organization_and_account(organization_uid=organization)
        ok_to_start_trial = typer.confirm(
            f"You are about to start trial of RemotiveTopology for {valid_organization.display_name}"
            f" (uid={valid_organization.uid}), continue?",
            default=True,
        )
        if not ok_to_start_trial:
            return

        (subscription, created) = start_trial(organization)

        def print_start_trial_result() -> None:
            assert subscription.type in ("trial", "paid"), f"Unexpected subscription type: {subscription.type}"
            kind = None
            status = None
            if subscription.type == "trial":
                status = "started now" if created else "is already active"
                kind = "trial subscription"
            elif subscription.type == "paid":
                status = "started now" if created else "is already started"
                kind = "subscription"

            end_text = subscription.end_date or "Never"
            print_generic_message(f"RemotiveTopology {kind} for {valid_organization.display_name} {status}, expires {end_text}")

        print_start_trial_result()

    except NotSignedInError:
        print_generic_error(
            "You must first sign in to RemotiveCloud, please use [bold]remotive cloud auth login[/bold] to sign-in"
            "This requires a RemotiveCloud account, if you do not have an account you can sign-up at https://cloud.remotivelabs.com"
        )
        raise typer.Exit(2)

    except NoActiveAccountError:
        print_hint(
            "You have not activated your account, please run [bold]remotive cloud auth activate[/bold] to choose an account"
            "or [bold]remotive cloud auth login[/bold] to sign-in"
        )
        raise typer.Exit(3)

    except NotAuthorizedError:
        print_hint(
            "Your current active credentials are not valid, please run [bold]remotive cloud auth login[/bold] to sign-in again."
            "This requires a RemotiveCloud account, if you do not have an account you can sign-up at https://cloud.remotivelabs.com"
        )
        raise typer.Exit(4)

    except MissingOrganizationError:
        print_hint("You have not specified any organization and no default organization is set")
        raise typer.Exit(5)

    except NotAuthorizedToStartTrialError as e:
        print_generic_error(f"You are not allowed to start-trial topology in organization {e.organization.display_name}.")
        raise typer.Exit(6)

    except SubscriptionExpiredError as e:
        if e.subscription.type == "trial":
            print_generic_error(
                f"RemotiveTopology trial in {e.organization.display_name} expired"
                f" {e.subscription.end_date}, please contact support@remotivelabs.com"
            )
            raise typer.Exit(7)

        print_generic_error(
            f"RemotiveTopology subscription in {e.organization.display_name} has expired"
            f" {e.subscription.end_date}, please contact support@remotivelabs.com"
        )
        raise typer.Exit(7)

    except NoOrganizationOrPermissionError as e:
        print_generic_error(f"Organization id {e.organization} does not exist or you do not have permission to access it.")
        raise typer.Exit(7)

    except Exception as e:
        print_generic_error(f"Unexpected error: {e}")
        raise typer.Exit(1)
