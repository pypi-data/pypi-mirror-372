# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class OAuth2CallbackController(http.Controller):
    @http.route(["/oauth2/callback"], type="http", auth="user", csrf=False)
    def oauth2_callback(self, **kwargs):
        full_url = request.httprequest.url
        _logger.info("OAuth2 callback received: %s", full_url)

        auth_rec = (
            request.env["webhook.auth"]
            .sudo()
            .search(
                [
                    ("type", "=", "oauth2"),
                    ("grant_type", "=", "authorization_code"),
                ],
                order="id desc",
                limit=1,
            )
        )

        if not auth_rec:
            return request.render(
                "web.oauth2_error",
                {
                    "message": _(
                        "No webhook.auth record found for "
                        "grant_type=authorization_code."
                    )
                },
            )

        try:
            auth_rec.authorization_response = full_url
            auth_rec.action_fetch_token()

            return {
                "type": "ir.actions.act_window",
                "res_model": "webhook.auth",
                "res_id": auth_rec.id,
                "view_mode": "form",
                "target": "current",
                "tag": "reload",
                "context": {
                    "default_id": auth_rec.id,
                },
                "params": {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("OAuth2 Success"),
                        "message": _("Authorization successful, token saved."),
                        "type": "success",
                        "sticky": False,
                    },
                },
            }

        except Exception as e:
            _logger.exception("OAuth2 callback error")
            return {
                "type": "ir.actions.act_window",
                "res_model": "webhook.auth",
                "view_mode": "tree,form",
                "target": "current",
                "params": {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("OAuth2 Error"),
                        "message": str(e),
                        "type": "danger",
                        "sticky": True,
                    },
                },
            }
