# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class WebHookHistory(models.Model):
    _name = "webhook_history"
    _description = "Webhook Histories"
    _order = "create_date desc"

    webhook_id = fields.Many2one(
        string="# Webhook",
        comodel_name="webhook_base",
        ondelete="cascade",
        required=True,
    )
    state = fields.Selection(
        string="Status",
        selection=[
            ("success", "Success"),
            ("failed", "Failed"),
        ],
        required=True,
    )
    user_id = fields.Many2one(
        string="Responsible",
        comodel_name="res.users",
        required=True,
    )
    context_data = fields.Text(string="Context Data")
    request = fields.Text(string="Request")
    response = fields.Text(string="Response")
    result = fields.Text(string="Result")
    exception = fields.Text(string="Exception")
    traceback = fields.Text(string="Traceback")
