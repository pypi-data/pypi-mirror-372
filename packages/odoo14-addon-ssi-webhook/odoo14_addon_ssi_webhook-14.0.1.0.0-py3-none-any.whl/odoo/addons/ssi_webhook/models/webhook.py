# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import json
import logging
import re
import textwrap
import traceback

import odoo
from odoo import SUPERUSER_ID, _, api, fields, models, registry, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools import config, mute_logger, ustr
from odoo.tools.float_utils import float_compare
from odoo.tools.safe_eval import safe_eval, test_python_expr
from pytz import timezone
from requests import Session

_logger = logging.getLogger(__name__)


def _truncate_structure(obj, limit):
    if limit is None or limit <= 0:
        return obj
    if isinstance(obj, str):
        return obj if len(obj) <= limit else obj[:limit] + "..."
    if isinstance(obj, dict):
        return {k: _truncate_structure(v, limit) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_truncate_structure(v, limit) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_truncate_structure(v, limit) for v in obj)
    return obj


class WebHookBase(models.Model):
    _name = "webhook_base"
    _description = "Webhook"
    _inherit = ["mixin.master_data"]

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self._default_company_id(),
        copy=True,
    )
    code = fields.Char(
        default="/",
    )
    action_id = fields.Many2one(
        string="Server Action",
        comodel_name="ir.actions.server",
        ondelete="cascade",
    )
    model_id = fields.Many2one(
        string="Model",
        comodel_name="ir.model",
        required=True,
        ondelete="cascade",
        index=True,
        help="Model on which the webhook runs.",
    )
    model_name = fields.Char(
        string="Model Name",
        related="model_id.model",
        readonly=True,
        store=True,
    )
    use_auth = fields.Boolean(
        string="Use Authentication",
        default=False,
    )
    webhook_auth_id = fields.Many2one(
        string="Authentication",
        comodel_name="webhook_auth",
        ondelete="restrict",
    )
    webhook_address = fields.Char(
        string="Address",
        required=True,
    )
    webhook_method = fields.Selection(
        string="Method",
        selection=[
            ("GET", "GET"),
            ("POST", "POST"),
            ("PUT", "PUT"),
            ("DELETE", "DELETE"),
        ],
        default="POST",
        required=True,
    )
    webhook_timeout = fields.Integer(
        string="Timeout",
        default=30,
    )

    use_header_code = fields.Boolean(
        string="Use Headers",
        default=False,
    )
    python_header_code = fields.Text(
        string="Header Code",
        default=textwrap.dedent(
            """
# Available variables:
#
#  - user: User who triggered the action
#  - result: Current headers of the request
#  - env: Odoo Environment on which the action is triggered
#  - model: Odoo Model of the record on which the action is triggered;
#    is a void recordset
#  - record: Record on which the action is triggered; may be void
#  - records: Recordset of all records on which the action is
#    triggered in multi-mode; may be void
#  - time, datetime, dateutil, timezone, json: Useful Python
#    libraries
#  - b64encode, b64decode: Base64 converter to encode and decode
#    binary data
#  - UserError: Warning Exception to use with raise
#
result = {}"""
        ),
    )

    use_payload_code = fields.Boolean(
        string="Use Payloads",
        default=False,
    )
    python_payload_code = fields.Text(
        string="Payload Code",
        default=textwrap.dedent(
            """
# Available variables:
#
#  - user: User who triggered the action
#  - env: Odoo Environment on which the action is triggered
#  - model: Odoo Model of the record on which the action is triggered;
#    is a void recordset
#  - record: Record on which the action is triggered; may be void
#  - records: Recordset of all records on which the action is
#    triggered in multi-mode; may be void
#  - time, datetime, dateutil, timezone, json: Useful Python
#    libraries
#  - b64encode, b64decode: Base64 converter to encode and decode
#    binary data
#  - UserError: Warning Exception to use with raise
#
result = {}"""
        ),
    )
    history_ids = fields.One2many(
        string="Histories",
        comodel_name="webhook_history",
        inverse_name="webhook_id",
    )

    use_response_code = fields.Boolean(
        string="Use Response",
        default=False,
    )

    python_response_code = fields.Text(
        string="Response",
        default=textwrap.dedent(
            """
# Process the response of the request.
#
# Available variables:
#
#  - user: User who triggered the action
#  - request: Request send by the action
#  - response: Response received when the request was sent
#  - env: Odoo Environment on which the action is triggered
#  - model: Odoo Model of the record on which the action is triggered;
#    is a void recordset
#  - record: Record on which the action is triggered; may be void
#  - records: Recordset of all records on which the action is
#    triggered in multi-mode; may be void
#  - time, datetime, dateutil, timezone, json: Useful Python
#    libraries
#  - b64encode, b64decode: Base64 converter to encode and decode
#    binary data
#  - UserError: Warning Exception to use with raise
#
result = {}"""
        ),
    )

    @api.depends(
        "history_ids",
    )
    def _compute_latest_history_id(self):
        for record in self:
            record.latest_history_id = False

            if record.history_ids:
                latest = self.env["webhook_history"].search(
                    [("webhook_id", "=", record.id)], limit=1, order="id desc"
                )
                if latest:
                    record.latest_history_id = latest

    latest_history_id = fields.Many2one(
        string="Latest History",
        comodel_name="webhook_history",
        compute="_compute_latest_history_id",
        store=True,
        readonly=True,
    )

    @api.model
    def _get_localdict(self):
        model = self.env[self.model_name]
        active_id = self.env.context.get("active_id", False)
        active_ids = self.env.context.get("active_ids", [])
        return {
            "self": self,
            "model": model,
            "record": model.browse(active_id),
            "records": model.browse(active_ids),
            "uid": self._uid,
            "user": self.env.user,
            "time": tools.safe_eval.time,
            "datetime": tools.safe_eval.datetime,
            "dateutil": tools.safe_eval.dateutil,
            "timezone": timezone,
            "float_compare": float_compare,
            "b64encode": base64.b64encode,
            "b64decode": base64.b64decode,
            "json": tools.safe_eval.json,
            "context": self.env.context,
            # Exceptions
            "Warning": odoo.exceptions.Warning,
            "UserError": odoo.exceptions.UserError,
        }

    def _execute_webhook(self):
        self.ensure_one()
        webhook_session = response = request = exception = None
        localdict = self._get_localdict()
        try:
            with self.env.cr.savepoint():
                webhook_session = self._get_webhoook_session()
                headers = self._get_webhook_headers(localdict)
                datas = self._get_webhook_data(localdict)

                data = {"data": datas}
                if self.check_json_content_type(headers):
                    data = {"json": datas}

                response = webhook_session.request(
                    self.webhook_method,
                    self.webhook_address,
                    headers=headers,
                    timeout=self.webhook_timeout,
                    **data,
                )

                request = getattr(response, "request", None)

                if response is not None:
                    status = getattr(response, "status_code", None)
                    try:
                        if status is not None:
                            try:
                                status_int = int(status)
                            except Exception:
                                status_int = None
                            if status_int is not None and status_int >= 400:
                                try:
                                    from requests import HTTPError

                                    err_msg = f"HTTP {status_int} error"
                                    exception = HTTPError(err_msg)
                                except Exception:
                                    err_msg = f"HTTP {status_int} error"
                                    exception = Exception(err_msg)
                    except Exception:
                        pass
        except Exception as err:
            exception = err
        finally:
            if webhook_session is not None:
                webhook_session.close()
        return (request, response, exception, localdict)

    def _run_webhook(self):
        self.ensure_one()
        request, response, exception, localdict = self._execute_webhook()

        history = self._create_history(
            eval_context=localdict,
            request=request,
            response=response,
            exception=exception,
        )
        return history

    def _get_webhoook_session(self):
        self.ensure_one()
        if self.webhook_auth_id:
            return self.webhook_auth_id._get_auth_session()
        return Session()

    def _get_webhook_headers(self, localdict):
        self.ensure_one()
        result = {}

        if self.use_header_code and self.python_header_code:
            try:
                safe_eval(
                    self.python_header_code.strip(),
                    localdict,
                    mode="exec",
                    nocopy=True,
                )
                result = localdict["result"]
            except Exception as error:
                raise UserError(_("Error evaluating conditions.\n %s") % error)
        return result

    def _get_webhook_data(self, localdict):
        self.ensure_one()
        result = {}

        if self.use_payload_code and self.python_payload_code:
            try:
                safe_eval(
                    self.python_payload_code.strip(),
                    localdict,
                    mode="exec",
                    nocopy=True,
                )
                result = localdict["result"]
            except Exception as error:
                raise UserError(_("Error evaluating conditions.\n %s") % error)
        return result

    def _limit(self, text):
        self.ensure_one()
        if text is None:
            return None
        limit = int(config.get("webhook_logging_attribute_limit", 150))
        s = ustr(text)
        return s if not limit or len(s) <= limit else s[:limit] + "..."

    def _serialize_request(self, r):
        self.ensure_one()
        if r is None:
            return None
        try:
            headers = {}
            url = getattr(r, "url", None)
            method = getattr(r, "method", None)

            try:
                hdrs = getattr(r, "headers", None)
                headers = dict(hdrs or {})
            except Exception:
                if isinstance(r, dict) and "headers" in r:
                    try:
                        headers = dict(r.get("headers") or {})
                    except Exception:
                        headers = {}

            body = None
            if isinstance(r, dict):
                for k in ("body", "data", "json", "payload"):
                    if k in r:
                        body = r.get(k)
                        break
            else:
                for k in ("body", "data", "_content", "json", "payload"):
                    if hasattr(r, k):
                        body = getattr(r, k)
                        break

            if isinstance(body, bytes):
                body = body.decode("utf-8", errors="replace")

            parsed_body = None
            if body is not None and body != "":
                try:
                    parsed_body = json.loads(body)
                except Exception:
                    parsed_body = self._limit(body)

            if (
                not method
                and not url
                and not headers
                and parsed_body in (None, "")  # noqa: E501
            ):
                srepr = ustr(r)
                m = re.search(r"\[([A-Z]+)\]", srepr)
                if m:
                    method = m.group(1)
                    return {
                        "method": method,
                        "url": None,
                        "headers": {},
                        "body": None,
                        "repr": srepr,
                    }

            return {
                "method": method,
                "url": url,
                "headers": headers,
                "body": parsed_body,
            }
        except Exception:
            return {"repr": self._limit(ustr(r))}

    def _serialize_response(self, resp, eval_context):
        self.ensure_one()
        if resp is None:
            return None
        if self.use_response_code and self.python_response_code:
            resp_context = eval_context.copy()
            resp_context.update({"response": resp})
            safe_eval(
                self.python_response_code.strip(),
                resp_context,
                mode="exec",
                nocopy=True,
            )
            if "result" in resp_context:
                return resp_context["result"]
        else:
            try:
                hdrs = getattr(resp, "headers", None)
                try:
                    headers = dict(hdrs or {})
                except Exception:
                    headers = {}
                text = None
                try:
                    if hasattr(resp, "json"):
                        text = resp.json()
                    else:
                        text = getattr(resp, "text", None)
                except Exception:
                    text = self._limit(getattr(resp, "text", None))
                return {
                    "status_code": getattr(resp, "status_code", None),
                    "reason": getattr(resp, "reason", None),
                    "headers": headers,
                    "text": text,
                    "full_resp": resp,
                }
            except Exception:
                return self._limit(ustr(resp))

    def _get_history(
        self, request=None, response=None, exception=None, eval_context=None
    ):
        self.ensure_one()
        vals = {
            "request": self._serialize_request(request),
            "response": self._serialize_response(response, eval_context),
            "exception": None,
            "traceback": None,
        }
        if isinstance(exception, BaseException):
            try:
                exc_type = type(exception).__name__
                exc_msg = ustr(exception)
                short_msg = f"{exc_type}: {exc_msg}"
                full_tb = "".join(
                    traceback.format_exception(
                        type(exception), exception, exception.__traceback__
                    )
                )
            except Exception:
                short_msg = ustr(exception)
                full_tb = short_msg

            vals["exception"] = self._limit(short_msg)
            vals["traceback"] = full_tb
        elif exception:
            vals["exception"] = self._limit(ustr(exception))

        ctx = eval_context or {}
        vals["context_data"] = json.dumps(
            {
                "active_model": getattr(ctx.get("model"), "_name", False),
                "active_id": getattr(ctx.get("record"), "id", False),
                "active_ids": getattr(ctx.get("records"), "ids", False),
            },
            indent=4,
            sort_keys=True,
        )
        return vals

    def _create_history(self, eval_context, request, response, exception):
        self.ensure_one()
        history_id = False
        vals = self._get_history(
            request=request,
            response=response,
            exception=exception,
            eval_context=eval_context,
        )
        history_vals = {**vals}
        limit = int(config.get("webhook_logging_attribute_limit", 150)) or None
        for key in ("request", "response"):
            try:
                val = history_vals.get(key)
                if val is None:
                    history_vals[key] = None
                else:
                    processed = _truncate_structure(val, limit)
                    history_vals[key] = json.dumps(
                        processed, indent=4, sort_keys=True, default=ustr
                    )
            except Exception:
                history_vals[key] = ustr(history_vals.get(key))
        if history_vals.get("exception") is not None:
            attribute_limit = (
                int(config.get("webhook_logging_attribute_limit", 150)) or None
            )
            history_vals["exception"] = ustr(history_vals["exception"])[
                :attribute_limit
            ]
        history_exc = history_vals.get("exception")
        history_vals.update(
            {
                "state": ("failed" if history_exc else "success"),
                "webhook_id": self.id,
                "user_id": self.env.uid,
            }
        )

        try:
            with mute_logger("odoo.sql_db"), registry(
                self.env.cr.dbname
            ).cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                history_id = env["webhook_history"].create(history_vals)
            return history_id
        except Exception as err:
            log_msg = "Failed to create webhook_history " "for webhook %s: %s"
            _logger.exception(log_msg) % (
                self.id,
                err,
            )

    def create_action(self):
        Action = self.env["ir.actions.server"]
        for record in self:
            name = f"[Webhook]: {record.name}"
            code = (
                "WebhookBase = env['webhook_base']\n"
                "WebhookBase.browse(%s)._run_webhook()\n"
                "action = False\n"
            ) % record.id
            vals = {
                "name": name,
                "state": "code",
                "model_id": record.model_id.id,
                "code": code,
                "binding_model_id": record.model_id.id,
                "binding_type": "action",
            }
            server_action = Action.create(vals)
            record.action_id = server_action

    def unlink_action(self):
        self.check_access_rights("write", raise_exception=True)
        acts = self.mapped("action_id").filtered("id")
        if self:
            self.write({"action_id": False})
        if acts:
            acts.unlink()

    @api.constrains(
        "python_header_code",
    )
    def _check_python_header_code(self):
        for record in self.sudo().filtered("python_header_code"):
            message = test_python_expr(
                expr=record.python_header_code.strip(), mode="exec"
            )
            if message:
                raise ValidationError(message)

    @api.constrains(
        "python_payload_code",
    )
    def _check_python_payload_code(self):
        for record in self.sudo().filtered("python_payload_code"):
            message = test_python_expr(
                expr=record.python_payload_code.strip(), mode="exec"
            )
            if message:
                raise ValidationError(message)

    @api.constrains(
        "python_response_code",
    )
    def _check_python_response_code(self):
        for record in self.sudo().filtered("python_response_code"):
            message = test_python_expr(
                expr=record.python_response_code.strip(), mode="exec"
            )
            if message:
                raise ValidationError(message)

    def check_json_content_type(self, headers):
        self.ensure_one()
        for key, value in headers.items():
            content_type_match = (
                key.lower() == "content-type"
                and value.lower() == "application/json"  # noqa: E501
            )
            if content_type_match:
                return True
        return False

    def action_refresh_latest_history(self):
        for record in self:
            record._compute_latest_history_id()
