// Copyright 2025 OpenSynergy Indonesia
// Copyright 2025 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
odoo.define("ssi_mail_telegram/static/src/components/mail_telegram.js", function (
    require
) {
    "use strict";

    const components = {
        Message: require("mail/static/src/components/message/message.js"),
    };
    const {patch} = require("web.utils");

    patch(components.Message, "ssi_mail_telegram.main", {
        async _onClickSendToTelegram(ev) {
            ev.stopPropagation();
            const action = await this.rpc({
                route: "/web/action/load",
                params: {action_id: "ssi_mail_telegram.send_telegram_action"},
            });
            action.context = {
                default_message_id: this.message.id,
            };
            this.env.bus.trigger("do-action", {action: action});
        },
    });
});
