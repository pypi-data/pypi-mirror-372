# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from requests.auth import HTTPBasicAuth


def basic_auth(user, password):
    res = HTTPBasicAuth(user, password)
    return res
