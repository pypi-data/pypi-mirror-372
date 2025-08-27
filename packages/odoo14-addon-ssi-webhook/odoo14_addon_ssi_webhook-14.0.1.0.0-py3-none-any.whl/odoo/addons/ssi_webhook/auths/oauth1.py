# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from requests_oauthlib import OAuth1


def oauth1_auth(
    client_id,
    client_secret,
    resource_owner_key,
    resource_owner_secret,
    signature_method,
):
    return OAuth1(
        client_key=client_id,
        client_secret=client_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        signature_method=signature_method,
    )
