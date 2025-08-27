# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models
from requests import Session

from ..auths import api_key, basic, digest, oauth1, oauth2


class WebHookAuth(models.Model):
    _name = "webhook_auth"
    _description = "Webhook Authentications"
    _inherit = ["mixin.master_data"]

    code = fields.Char(
        default="/",
    )
    type = fields.Selection(
        string="Types",
        selection=[
            ("api", "API Key"),
            ("basic", "Basic Authentication"),
            ("oauth1", "OAuth 1.0a"),
            ("oauth2", "Bearer Token / OAuth 2.0"),
            ("digest", "Digest Authentication"),
        ],
        required=True,
        default="basic",
    )
    # BASIC
    username = fields.Char(
        string="Username",
        copy=False,
    )
    password = fields.Char(
        string="Password",
        copy=False,
    )

    # OAuth2 credentials
    grant_type = fields.Selection(
        string="Grant Type",
        selection=[
            ("client_credentials", "Client Credentials"),
            ("password", "Password"),
        ],
        default="client_credentials",
    )
    client_id = fields.Char(
        string="Client ID",
        copy=False,
    )
    client_secret = fields.Char(
        string="Client Secret",
        copy=False,
    )
    token_url = fields.Char(
        string="Token URL",
        copy=False,
    )

    # API Key
    api_key = fields.Char(string="API Key")

    # OAuth1 credentials
    signature_method = fields.Selection(
        string="Method",
        selection=[
            ("HMAC-SHA1", "HMAC-SHA1"),
            ("RSA-SHA1", "RSA-SHA1"),
        ],
        default="HMAC-SHA1",
    )
    resource_owner_key = fields.Char(
        string="Res. Owner Key",
        copy=False,
    )
    resource_owner_secret = fields.Char(
        string="Res. Owner Secret",
        copy=False,
    )

    def _get_auth_session(self):
        session = Session()
        if self.type == "basic":
            session.auth = basic.basic_auth(self.username, self.password)
            return session
        elif self.type == "digest":
            session.auth = digest.digest_auth(self.username, self.password)
            return session
        elif self.type == "oauth2":
            if self.grant_type == "password":
                return oauth2.password(
                    token_url=self.token_url,
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    username=self.username,
                    password=self.password,
                )
            elif self.grant_type == "client_credentials":
                return oauth2.client_credentials(
                    token_url=self.token_url,
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                )
        elif self.type == "oauth1":
            return oauth1.oauth1_auth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                resource_owner_key=self.resource_owner_key,
                resource_owner_secret=self.resource_owner_secret,
            )
        elif self.type == "api":
            return api_key.ApiKey(self.api_key)
        return Session()
