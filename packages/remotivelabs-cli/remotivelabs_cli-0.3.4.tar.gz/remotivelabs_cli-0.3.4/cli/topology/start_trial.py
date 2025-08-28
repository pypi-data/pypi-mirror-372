from __future__ import annotations

import datetime
from dataclasses import dataclass
from datetime import date
from typing import Any

from cli.settings import settings
from cli.settings.config_file import Account
from cli.utils.rest_helper import RestHelper
from cli.utils.time import parse_date


class NoActiveAccountError(Exception):
    """Raised when the user has no active account, but there are available accounts to activate"""


class NotSignedInError(Exception):
    """Raised when the user has no active account, and no available accounts to activate"""


class NotAuthorizedError(Exception):
    """Raised when the user is not authorized"""

    def __init__(self, account: Account):
        self.account = account


class NoOrganizationOrPermissionError(Exception):
    """Raised when the user is trying to access an organization that it does not have access to or it does not exist"""

    def __init__(self, account: Account, organization_uid: str):
        self.account = account
        self.organization = organization_uid


class MissingOrganizationError(Exception):
    """Raised when the user has not specified an organization and no default organization is set"""


class NotAuthorizedToStartTrialError(Exception):
    """Raised when the user is not authorized to start a topology trial"""

    def __init__(self, account: Account, organization: Organization):
        self.account = account
        self.organization = organization


class SubscriptionExpiredError(Exception):
    """Raised when the subscription has expired"""

    def __init__(self, subscription: Subscription, organization: Organization):
        self.subscription = subscription
        self.organization = organization


@dataclass
class Organization:
    uid: str
    display_name: str


@dataclass
class Subscription:
    type: str
    display_name: str
    feature: str
    start_date: date
    end_date: date

    @staticmethod
    def from_dict(data: Any) -> Subscription:
        if not isinstance(data, dict):
            raise ValueError(f"Invalid subscription data {data}")

        return Subscription(
            type=data["subscriptionType"],
            display_name=data["displayName"],
            feature=data["feature"],
            start_date=parse_date(data["startDate"]),
            end_date=parse_date(data["endDate"]),
        )


def get_organization_and_account(organization_uid: str | None = None) -> tuple[Organization, Account]:
    active_account = settings.get_active_account()
    active_token_file = settings.get_active_token_file()

    if not active_account or not active_token_file:
        if len(settings.list_accounts()) == 0:
            raise NotSignedInError()
        raise NoActiveAccountError()

    if not RestHelper.has_access("/api/whoami"):
        raise NotAuthorizedError(account=active_account)

    org_uid = organization_uid or active_account.default_organization
    if not org_uid:
        raise MissingOrganizationError()

    response = RestHelper.handle_get(f"/api/bu/{organization_uid}", return_response=True, allow_status_codes=[403, 404])
    if response.status_code in (403, 404):
        raise NoOrganizationOrPermissionError(account=active_account, organization_uid=org_uid)

    display_name = response.json()["displayName"]

    return Organization(uid=org_uid, display_name=display_name), active_account


def start_trial(organization_uid: str | None = None) -> tuple[Subscription, bool]:
    """
    Start a 30 day trial subscription for running RemotiveTopology,
    If a trial is already started in this organization, returns the existing trial instead.
    Returns (subscription, created_now).
    """

    (organization, active_account) = get_organization_and_account(organization_uid)

    res = RestHelper.handle_get(f"/api/bu/{organization.uid}/features/topology", return_response=True, allow_status_codes=[403, 404])
    if res.status_code == 403:
        raise NotAuthorizedToStartTrialError(account=active_account, organization=organization)

    created_now = False
    if res.status_code == 404:
        created = RestHelper.handle_post(f"/api/bu/{organization.uid}/features/topology", return_response=True)
        subscription = Subscription.from_dict(created.json())
        created_now = True
    else:
        subscription = Subscription.from_dict(res.json())

    if subscription.end_date < datetime.datetime.now().date():
        raise SubscriptionExpiredError(subscription=subscription, organization=organization)

    return subscription, created_now
