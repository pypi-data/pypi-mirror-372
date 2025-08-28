# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=C8101
{
    "name": "SSI - Mail Telegram",
    "version": "14.0.1.0.0",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "ssi_telegram",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/mail_message_views.xml",
        "wizards/send_telegram.xml",
    ],
    "qweb": [
        "static/src/components/mail_telegram.xml",
    ],
    "external_dependencies": {
        "python": [
            "beautifulsoup4",
            "bleach",
        ],
    },
}
