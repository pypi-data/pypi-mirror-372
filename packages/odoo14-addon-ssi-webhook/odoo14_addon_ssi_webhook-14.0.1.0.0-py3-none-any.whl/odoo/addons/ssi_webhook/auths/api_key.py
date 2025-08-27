# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import requests


class ApiKey(requests.auth.AuthBase):
    def __init__(self, apikey):
        self.apikey = apikey

    def __eq__(self, other):
        return all([self.apikey == getattr(other, "apikey", None)])

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers["Authorization"] = "ApiKey {}".format(self.apikey)
        return r
