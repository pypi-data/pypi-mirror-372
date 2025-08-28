# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class MailMessageTelegram(models.Model):
    _name = "mail.message.telegram"
    _description = "Telegram Link for Mail Message"
    _order = "create_date desc"

    message_id = fields.Many2one(
        string="Message",
        comodel_name="mail.message",
        required=True,
        ondelete="cascade",
        index=True,
    )
    chat_id = fields.Char(
        string="Telegram Chat ID",
        required=True,
    )
    telegram_message_id = fields.Char(
        string="Telegram Message ID",
        required=True,
    )
    chat_username = fields.Char(
        string="Username/Handle",
        help="Username or handle of the Telegram chat (e.g., @channelname)",
    )

    def get_telegram_url(self):
        self.ensure_one()
        if self.chat_username:
            username = self.chat_username.replace("@", "")
            return f"https://t.me/{username}/{self.telegram_message_id}"

        chat_id = str(self.chat_id)
        if chat_id.startswith("-100"):
            clean_chat_id = chat_id[4:]
            return f"https://t.me/c/{clean_chat_id}/{self.telegram_message_id}"
        elif chat_id.startswith("-"):
            return None
        else:
            return f"https://t.me/c/{chat_id}/{self.telegram_message_id}"

    @api.model
    def get_message_telegram_links(self, message_ids):
        """API method to get telegram links for messages"""
        telegram_links = self.search([("message_id", "in", message_ids)])
        result = {}
        for link in telegram_links:
            if link.message_id.id not in result:
                result[link.message_id.id] = []

            url = link.get_telegram_url()
            can_link = url is not None

            chat_description = "Unknown Chat"
            if link.chat_id:
                backend_chat = self.env["telegram_backend_chat"].search(
                    [("name", "=", link.chat_id)], limit=1
                )
                if backend_chat:
                    chat_description = backend_chat.description or backend_chat.name

            result[link.message_id.id].append(
                {
                    "chat_id": link.chat_id,
                    "telegram_message_id": link.telegram_message_id,
                    "url": url,
                    "can_link": can_link,
                    "chat_description": chat_description,
                }
            )
        return result
