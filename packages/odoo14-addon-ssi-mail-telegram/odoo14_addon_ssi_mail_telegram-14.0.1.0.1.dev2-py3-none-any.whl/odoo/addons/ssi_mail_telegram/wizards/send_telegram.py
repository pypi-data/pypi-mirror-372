# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# pylint: disable=invalid-commit
import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SendTelegram(models.TransientModel):
    _name = "send_telegram"
    _description = "Send Message to Telegram"

    @api.model
    def _get_telegram_backend_id(self):
        company = self.env.company
        backend = company.telegram_backend_id
        return backend and backend.id or False

    backend_id = fields.Many2one(
        string="Backend",
        comodel_name="telegram_backend",
        default=lambda self: self._get_telegram_backend_id(),
        required=True,
    )

    @api.depends("backend_id")
    def _compute_allowed_chat_ids(self):
        BackendChat = self.env["telegram_backend_chat"]
        for wizard in self:
            if wizard.backend_id:
                chat_ids = BackendChat.search(
                    [("backend_id", "=", wizard.backend_id.id)]
                )
                wizard.allowed_chat_ids = chat_ids
            else:
                wizard.allowed_chat_ids = False

    allowed_chat_ids = fields.Many2many(
        string="Allowed Chat ID's",
        comodel_name="telegram_backend_chat",
        compute="_compute_allowed_chat_ids",
        relation="rel_send_telegram_2_backend_chat",
        column1="wizard_id",
        column2="chat_id",
    )

    chat_id = fields.Many2one(
        string="Chat ID",
        comodel_name="telegram_backend_chat",
        required=True,
    )

    @api.model
    def _default_message_id(self):
        message_id = self.env.context.get("default_message_id", "")
        return message_id

    message_id = fields.Many2one(
        comodel_name="mail.message",
        string="Message",
        default=lambda self: self._default_message_id(),
    )

    def _get_telegram_message_id(self, history):
        self.ensure_one()
        result = False

        if history.state == "success":
            try:
                response_content = history.response
                if isinstance(response_content, str):
                    response = json.loads(response_content)
                else:
                    response = response_content

                if isinstance(response, dict):
                    if "telegram_message_id" in response:
                        result = response["telegram_message_id"]
                    elif "result" in response and isinstance(response["result"], dict):
                        if "telegram_message_id" in response["result"]:
                            result = response["result"]["telegram_message_id"]
                        elif "message_id" in response["result"]:
                            result = response["result"]["message_id"]
                    elif "message_id" in response:
                        result = response["message_id"]
                    else:
                        msg_err = _(
                            "No 'telegram_message_id'/'message_id' found in response."
                        )
                        raise UserError(msg_err)

            except (json.JSONDecodeError, TypeError):
                result = False
        return result

    def _prepare_mail_message_telegram_data(self, telegram_message_id):
        self.ensure_one()
        return {
            "message_id": self.message_id.id,
            "chat_id": self.chat_id.name,
            "telegram_message_id": telegram_message_id,
            "chat_username": self.chat_id.username,
        }

    def action_send(self):
        MailMessageTelegram = self.env["mail.message.telegram"]

        existing = MailMessageTelegram.search(
            [
                ("message_id", "=", self.message_id.id),
                ("chat_id", "=", self.chat_id.name),
            ]
        )
        if existing:
            msg_err = _("Message has already been sent to this chat.")
            raise UserError(msg_err)

        ctx = {
            "active_id": self.message_id.id,
            "active_ids": [self.message_id.id],
            "chat_id": self.chat_id.name,
            "bot_token": self.backend_id.bot_token,
        }

        webhook = self.backend_id.send_webhook_id
        webhook.with_context(ctx)._run_webhook()

        self.env.cr.commit()

        webhook._compute_latest_history_id()

        latest_history = self.env["webhook_history"].search(
            [
                ("webhook_id", "=", webhook.id),
            ],
            limit=1,
            order="id desc",
        )

        if not latest_history:
            msg_err = _("No successful webhook history found.")
            raise UserError(msg_err)

        if latest_history.context_data:
            try:
                context_data = json.loads(latest_history.context_data)
                if context_data.get("active_id") != self.message_id.id:
                    pass
            except json.JSONDecodeError:
                pass

        if latest_history.state == "success":
            telegram_message_id = self._get_telegram_message_id(latest_history)
            if telegram_message_id:
                MailMessageTelegram.create(
                    self._prepare_mail_message_telegram_data(telegram_message_id)
                )
            else:
                msg_err = _("Failed to get telegram_message_id from webhook response.")
                raise UserError(msg_err)

            return {
                "type": "ir.actions.client",
                "tag": "reload",
            }
        else:
            error_message = _(
                "Failed to send message to Telegram. "
                "Please check the webhook configuration and try again."
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Telegram Send Failed"),
                    "message": error_message,
                    "type": "danger",
                    "sticky": False,
                },
            }
