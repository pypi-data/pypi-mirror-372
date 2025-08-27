# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from requests.auth import HTTPDigestAuth


def digest_auth(user, password):
    res = HTTPDigestAuth(user, password)
    return res
