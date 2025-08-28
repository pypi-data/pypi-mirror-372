# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import re

import bleach
from bs4 import BeautifulSoup

from odoo import fields, models


class MailMessage(models.Model):
    _inherit = "mail.message"

    telegram_ids = fields.One2many(
        string="Telegrams",
        comodel_name="mail.message.telegram",
        inverse_name="message_id",
    )

    def convert_html_to_telegram(self, html: str) -> str:
        """
        Convert HTML email/text into Telegram-friendly HTML format.
        - Keeps only Telegram supported tags (<b>, <i>, <u>, <code>, <a>).
        - Converts <strong> -> <b>, <em> -> <i>.
        - Converts <br> -> \n, <p>/<div>/<ul>/<li> -> \n.
        - Removes duplicate newlines.
        """
        if not html:
            return ""

        soup = BeautifulSoup(html, "html.parser")

        # Normalisasi tag
        for strong in soup.find_all("strong"):
            strong.name = "b"
        for em in soup.find_all("em"):
            em.name = "i"
        for br in soup.find_all("br"):
            br.replace_with("\n")
        for p in soup.find_all(["p", "div", "ul", "li"]):
            p.insert_before("\n")

        # Bersihkan atribut (style, class, dsb.)
        for tag in soup.find_all(True):
            tag.attrs = {}

        # Allowed tags Telegram
        allowed_tags = ["b", "i", "u", "code", "a"]

        # Hapus tag lain
        for tag in soup.find_all(True):
            if tag.name not in allowed_tags:
                tag.unwrap()

        # Bleach sanitasi akhir
        clean_html = bleach.clean(
            str(soup), tags=allowed_tags, attributes={"a": ["href"]}, strip=True
        )

        # Rapikan newline → maksimal 1 baris kosong
        clean_html = re.sub(r"\n\s*\n+", "\n\n", clean_html)

        return clean_html.strip()

    def message_format(self):
        res = super().message_format()

        message_by_id = {m.id: m for m in self}
        for vals in res:
            msg = message_by_id.get(vals["id"])
            if msg:
                telegram_data = [
                    {
                        "id": tg.id,
                        "chat_id": tg.chat_id,
                        "telegram_message_id": tg.telegram_message_id,
                    }
                    for tg in msg.telegram_ids
                ]
                vals["telegram_ids"] = telegram_data
        return res
